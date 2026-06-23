"""
Модуль dependency injection (Dishka providers).

Отвечает за:
- создание DB engine
- создание sessionmaker
- создание Redis клиента
- сборку сервисов и репозиториев
"""

import logging
from typing import AsyncIterable

import redis.asyncio as redis
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
)

from src.auth.interfaces import IUserRepository
from src.auth.jwt import IJWT, JWT
from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.security import IPasswordHasher, BcryptHasher
from src.auth.service import UserService
from src.auth.session.storage import RedisSessionStorage, ISessionStorage
from src.core.settings import Settings
from src.storage.s3 import S3Client

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
            secret=settings.jwt_secret, expire_minutes=settings.jwt_expire_minutes
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
