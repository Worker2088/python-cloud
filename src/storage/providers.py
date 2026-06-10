import logging
from typing import AsyncIterable

import redis.asyncio as redis
from dishka import Provider, Scope, provide
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine

from src.auth.interfaces import IUserRepository
from src.auth.jwt import IJWT, JWT
from src.auth.models import User
from src.auth.repository import UserRepository
from src.auth.security import IPasswordHasher, BcryptHasher
from src.auth.service import UserService
from src.auth.session.storage import RedisSessionStorage, ISessionStorage
from src.core.settings import Settings
from src.storage.interfaces import IStorageRepository
from src.storage.repository import StorageRepository
from src.storage.s3 import S3Client
from src.storage.service import StorageService

logger = logging.getLogger(__name__)


class StorageProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def provide_storage_repo(self, session: AsyncSession) -> IStorageRepository:
        return StorageRepository(session=session)


    @provide(scope=Scope.REQUEST)
    def provide_storage_service(self,
                                repo: IStorageRepository,
                                session: ISessionStorage,
                                s3_client: S3Client,
                                ) -> StorageService:
        return StorageService(repo=repo, session=session, s3_client=s3_client)


    @provide(scope=Scope.APP)
    def provide_s3_client(
            self,
            settings: Settings,
    ) -> S3Client:
        return S3Client(
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            endpoint_url=settings.minio_endpoint,
            bucket_name=settings.minio_bucket_name,
        )

