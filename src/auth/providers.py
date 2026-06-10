import logging
from typing import AsyncIterable

import redis.asyncio as redis
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine

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
    # создаем движок БД
    @provide(scope=Scope.APP)
    def provide_engine(self, settings: Settings) -> AsyncEngine:
        logger.debug(
            "DB URL = %s",
            settings.db_url
        )
        engine = create_async_engine(
            url=settings.db_url,  # используем урл из настроек
            echo=True,
            pool_pre_ping=True
        )
        logger.debug("инициализировал движок БД, %s", engine.url.render_as_string(hide_password=True))
        return engine


    # фабрика сессий (async_sessionmaker)
    # Ей нужен engine, и Дишка сама заберет его из метода выше
    @provide(scope=Scope.APP)
    def provide_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        async_session = async_sessionmaker(
            bind=engine,
            expire_on_commit=False
        )
        logger.debug("создал фабрику сессий и подключил ее к движку БД, %s", async_session)
        return async_session


    # === ПЕРЕЕХАЛА ФУНКЦИЯ GET_SESSION ===
    # Вместо get_session теперь работает этот провайдер с Scope.REQUEST
    @provide(scope=Scope.REQUEST)
    async def provide_session(self, session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        logger.debug("запускаю сессию")

        # Вместо глобального async_session() вызываем session_maker(), который прилетел аргументом
        async with session_maker() as session:
            logger.debug("запустил сессию %s", session)
            yield session
            # Дишка "заморозит" генератор, отдаст сессию в репозиторий,
            # а после закрытия HTTP-запроса вернется сюда и закроет контекст-менеджер.
            logger.debug("закрыл сессию %s", session)


    # 2. Создаем репозиторий. Dishka увидит, что ему нужен session, и возьмет его выше.
    # Важно: указываем тип -> IUserRepository (наш Protocol), чтобы Dishka знала,
    # что этот класс закрывает потребность в интерфейсе.
    @provide(scope=Scope.REQUEST)
    def provide_user_repo(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session=session)


    # Фабрика для хэшера
    @provide(scope=Scope.APP)
    def provide_password_hasher(self) -> IPasswordHasher:
        return BcryptHasher()

    # работа с JWT
    @provide(scope=Scope.APP)
    def provide_jwt(self, settings: Settings) -> IJWT:
        return JWT(
            secret=settings.jwt_secret,
            expire_minutes=settings.jwt_expire_minutes
        )

    # 3. Создаем сервис. Dishka видит в аргументах IUserRepository
    # и автоматически подставит туда UserRepository.
    @provide(scope=Scope.REQUEST)
    def provide_user_service(self, repo: IUserRepository, hasher: IPasswordHasher, session: ISessionStorage) -> UserService:
        return UserService(repo=repo, hasher=hasher, session=session)


class InfrastructureProvider(Provider):

    @provide(scope=Scope.APP)
    async def provide_redis(self, settings: Settings) -> AsyncIterable[redis.Redis]:
        # Используем метод from_url и забираем строку подключения из настроек
        # Для прода это будет redis://redis:6379, а для тестов в conftest подменится на redis://localhost:6380
        logger.warning(
            "REDIS URL = %s",
            settings.redis_url
        )
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True,  )

        yield client

        await client.aclose()

    @provide(scope=Scope.APP)
    def provide_session_storage(self, redis: redis.Redis) -> ISessionStorage:
        return RedisSessionStorage(redis)


class IFileStorage:
    pass
class S3Storage:
    pass

# class IntegrationsProvider(Provider):
    # @provide(scope=Scope.REQUEST)
    # def provide_s3_storage(self) -> IFileStorage:
    #     return S3Storage(bucket_name="user-avatars")

