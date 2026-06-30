"""
Модуль dependency injection (Dishka providers).

Отвечает за:
- создание DB engine
- создание sessionmaker
- создание Redis клиента
- сборку сервисов и репозиториев
"""

import logging
from typing import AsyncIterable, Annotated

import redis.asyncio as redis
from dishka import Provider, Scope, provide
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)
from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer

from backend.auth.models import User
# from backend.auth.service import UserService
# from backend.auth.session.storage import ISessionStorage
from backend.core.request_context import user_id_ctx_var
from backend.storage.exception import UnauthorizedError
from backend.auth.interfaces import IUserRepository
from backend.auth.interfaces import IJWT
from backend.auth.jwt import JWT
from backend.auth.repository import UserRepository
from backend.auth.interfaces import IPasswordHasher
from backend.auth.security import BcryptHasher
from backend.auth.service import UserService
from backend.auth.interfaces import ISessionStorage
from backend.auth.session.storage import RedisSessionStorage
from backend.core.settings import Settings

logger = logging.getLogger(__name__)


class AdaptersProvider(Provider):
    """DI провайдер для инфраструктуры приложения."""

    @provide(scope=Scope.APP)
    def provide_engine(self, settings: Settings) -> AsyncEngine:
        """Создание SQLAlchemy engine."""

        engine = create_async_engine(
            url=settings.db_url,  # используем урл из настроек
            echo=True,
            pool_pre_ping=True,
        )
        logger.info(
            "инициализировал движок БД, %s",
            engine.url.render_as_string(hide_password=True),
        )
        return engine

    @provide(scope=Scope.APP)
    def provide_sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        """Фабрика DB сессий."""
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
        logger.info(
            "создал фабрику сессий и подключил ее к движку БД, %s", async_session
        )
        return async_session

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        """Создание request-scoped DB session."""
        async with session_maker() as session:
            logger.info("запустил сессию %s", session)
            yield session

            logger.info("закрыл сессию %s", session)

    @provide(scope=Scope.REQUEST)
    def provide_user_repo(self, session: AsyncSession) -> IUserRepository:
        """Репозиторий пользователей."""
        return UserRepository(session=session)

    @provide(scope=Scope.APP)
    def provide_password_hasher(self) -> IPasswordHasher:
        """Хэширование паролей."""
        return BcryptHasher()

    @provide(scope=Scope.APP)
    def provide_jwt(self, settings: Settings) -> IJWT:
        """JWT сервис."""
        return JWT(
            secret=settings.jwt_secret, expire_minutes=int(settings.jwt_expire_minutes)
        )

    @provide(scope=Scope.REQUEST)
    def provide_user_service(
        self, repo: IUserRepository, hasher: IPasswordHasher, session: ISessionStorage
    ) -> UserService:
        """UserService бизнес-логики."""
        return UserService(repo=repo, hasher=hasher, session=session)


class InfrastructureProvider(Provider):
    """DI провайдер инфраструктуры (Redis, S3 и т.д.)."""

    @provide(scope=Scope.APP)
    async def provide_redis(self, settings: Settings) -> AsyncIterable[redis.Redis]:
        """Redis клиент."""

        # Для прода это будет redis://redis:6379
        # для тестов в conftest подменится на redis://localhost:6380

        client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

        yield client

        await client.aclose()

    @provide(scope=Scope.APP)
    def provide_session_storage(self, redis: redis.Redis) -> ISessionStorage:
        """Хранилище сессий."""
        return RedisSessionStorage(redis)


@inject
async def get_current_user(
    sessions: FromDishka[ISessionStorage],
    service: FromDishka[UserService],
    session_id: str | None = Cookie(default=None),
) -> User:
    """
    Dependency для получения текущего авторизованного пользователя.

    Flow:
    1. Берём session_id из cookie
    2. Достаём user_id из Redis
    3. Загружаем User из БД
    4. Сохраняем user_id в ContextVar (для логирования)

    Raises:
        UnauthorizedError: если сессия отсутствует или невалидна

    Returns:
        User: текущий пользователь
    """

    if not session_id:
        raise UnauthorizedError()

    user_id = await sessions.get_user_id(session_id)

    if not user_id:
        raise UnauthorizedError()

    # Контекстная переменная с user_id (ContextVar)
    user_id_ctx_var.set(str(user_id))

    return await service.get_user_by_id(user_id)


CurrentUserDeps = Annotated[User, Depends(get_current_user)]


# --------------------------------------------
# реализация через JWT

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")

# @inject
# async def get_current_user(
#         token: Annotated[str, Depends(oauth2_scheme)],
#         service: FromDishka[UserService],
#         jwt: FromDishka[IJWT]
# ) -> User:
#     logger.debug("TOKEN RAW: %s", token)
#     user_id = jwt.decode_access_token(token)
#     logger.debug("user_id: %s", user_id)
#
#     if user_id is None:
#         raise HTTPException(401, "Invalid token")
#     logger.debug("!!!jwt.decode_access_token(token), user_id %s", user_id)
#
#     user = await service.get_user_by_id(user_id)
#
#     if user is None:
#         raise HTTPException(401, "User not found")
#     logger.debug("!!!service.get_user_by_id(user_id), username %s", user.username)
#
#     user_id_ctx_var.set(str(user_id))
#
#     return user
#
# CurrentUserDeps = Annotated[User, Depends(get_current_user)]