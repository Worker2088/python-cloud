"""
DI-провайдер Storage слоя (Dishka).

Отвечает за сборку:
- StorageRepository
- StorageService
- S3Client
"""

import logging

from dishka import Provider, Scope, provide

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.session.storage import ISessionStorage
from src.core.settings import Settings
from src.storage.interfaces import IStorageRepository
from src.storage.repository import StorageRepository
from src.storage.s3 import S3Client
from src.storage.service import StorageService

logger = logging.getLogger(__name__)


class StorageProvider(Provider):
    """
    DI контейнер для storage слоя.
    """

    @provide(scope=Scope.REQUEST)
    def provide_storage_repo(
        self, session: AsyncSession, s3client: S3Client
    ) -> IStorageRepository:
        """Создаёт репозиторий хранения объектов."""
        return StorageRepository(session=session, s3client=s3client)

    @provide(scope=Scope.REQUEST)
    def provide_storage_service(
        self,
        repo: IStorageRepository,
        session: ISessionStorage,
        s3_client: S3Client,
    ) -> StorageService:
        """Создаёт бизнес-сервис storage."""
        return StorageService(repo=repo, session=session, s3_client=s3_client)

    @provide(scope=Scope.APP)
    def provide_s3_client(self, settings: Settings) -> S3Client:
        """Создаёт S3 клиент (MinIO/AWS)."""
        return S3Client(
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            endpoint_url=settings.minio_endpoint,
            bucket_name=settings.minio_bucket_name,
        )
