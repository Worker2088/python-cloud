"""
Repository слой для работы с S3/MinIO.

Отвечает за:
- CRUD объектов в S3
- копирование/удаление
- получение metadata
- низкоуровневое взаимодействие с boto client
"""

import logging
from botocore.exceptions import ClientError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.storage.exception import (
    ObjectNotFoundError,
    StorageExternalError,
)
from backend.storage.s3 import S3Client

logger = logging.getLogger(__name__)


class StorageRepository:
    """
    Репозиторий для работы с S3 хранилищем.
    """

    def __init__(self, session: AsyncSession, s3client: S3Client):
        self.session = session
        self.s3client = s3client

    async def put_object(self, key: str, body: bytes = b"") -> str:
        """Создаёт объект в S3."""
        async with self.s3client.get_client() as client:
            await client.put_object(
                Bucket=self.s3client.bucket_name,
                Key=key,
                Body=body,
            )
        return key

    async def copy_object(self, from_key: str, to_key: str) -> str:
        """Копирует объект в S3."""
        async with self.s3client.get_client() as client:
            await client.copy_object(
                Bucket=self.s3client.bucket_name,
                CopySource={"Bucket": self.s3client.bucket_name, "Key": from_key},
                Key=to_key,
            )
        return to_key

    async def delete_object(self, s3_key: str) -> None:
        """Удаляет объект из S3."""
        try:
            async with self.s3client.get_client() as client:
                await client.delete_object(Bucket=self.s3client.bucket_name, Key=s3_key)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")

            if error_code in ("404", "NoSuchKey", "NoSuchBucket"):
                raise ObjectNotFoundError()

            raise StorageExternalError()

    async def delete_list_objects(self, s3_key: str) -> None:
        """Удаляет все объекты по префиксу (папка)."""
        async with self.s3client.get_client() as client:
            objects = await self.get_list_objects(s3_key)

            try:
                await client.delete_objects(
                    Bucket=self.s3client.bucket_name, Delete={"Objects": objects}
                )
            except ClientError:
                raise StorageExternalError()

    async def get_info_objects(self, s3_key: str) -> dict:
        """Возвращает metadata объекта."""
        async with self.s3client.get_client() as client:
            return await client.head_object(
                Bucket=self.s3client.bucket_name, Key=s3_key
            )

    async def object_exists(self, key: str) -> bool:
        """Проверяет существование объекта."""
        async with self.s3client.get_client() as client:
            try:
                await client.head_object(
                    Bucket=self.s3client.bucket_name,
                    Key=key,
                )
                return True
            except ClientError:
                return False

    async def get_list_objects_with_delimiter(self, key: str) -> dict:
        """Возвращает файлы и папки первого уровня."""
        if not key.endswith("/"):
            key += "/"

        async with self.s3client.get_client() as client:
            response = await client.list_objects_v2(
                Bucket=self.s3client.bucket_name, Prefix=key, Delimiter="/"
            )

        return {
            "files": response.get("Contents", []),
            "dirs": response.get("CommonPrefixes", []),
        }

    async def get_list_objects(self, key: str) -> list[dict]:
        """Возвращает все объекты по префиксу."""
        async with self.s3client.get_client() as client:
            response = await client.list_objects_v2(
                Bucket=self.s3client.bucket_name, Prefix=key
            )

        return [{"Key": item["Key"]} for item in response.get("Contents", [])]

    async def size_file(self, s3_key: str) -> int:
        """Возвращает размер файла."""
        async with self.s3client.get_client() as client:
            resp = await client.head_object(
                Bucket=self.s3client.bucket_name, Key=s3_key
            )
        return resp["ContentLength"]

    async def get_object(self, s3_key: str) -> bytes:
        """Читает содержимое объекта."""
        async with self.s3client.get_client() as client:
            resp = await client.get_object(
                Bucket=self.s3client.bucket_name,
                Key=s3_key,
            )
            return await resp["Body"].read()
