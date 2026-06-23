"""
S3 клиент (aiobotocore).

Обеспечивает async доступ к S3/MinIO через контекстный менеджер.
"""

from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from botocore.exceptions import ClientError


class S3Client:
    """
    Асинхронный клиент S3.
    """

    def __init__(
        self, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        """Контекстный менеджер S3 клиента."""
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def get_file(self, object_name: str, destination_path: str):
        """Скачивает файл на диск (локально)."""
        try:
            async with self.get_client() as client:
                response = await client.get_object(
                    Bucket=self.bucket_name, Key=object_name
                )
                data = await response["Body"].read()

            with open(destination_path, "wb") as file:
                file.write(data)

        except ClientError:
            print("Error downloading file")
