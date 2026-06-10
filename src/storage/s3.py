import asyncio
from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from botocore.exceptions import ClientError

# дополнительно установите pip install certifi, чтобы не было проблем с сертификатом


class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
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
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
            self,
            file_path: str,
    ):
        object_name = file_path.split("/")[-1]  # /users/artem/cat.jpg
        try:
            async with self.get_client() as client:
                with open(file_path, "rb") as file:
                    await client.put_object(
                        Bucket=self.bucket_name,
                        Key=object_name,
                        Body=file,
                    )
                print(f"File {object_name} uploaded to {self.bucket_name}")
        except ClientError as e:
            print(f"Error uploading file: {e}")

    async def delete_file(self, object_name: str):
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                print(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            print(f"Error deleting file: {e}")

    async def get_file(self, object_name: str, destination_path: str):
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                data = await response["Body"].read()
                with open(destination_path, "wb") as file:
                    file.write(data)
                print(f"File {object_name} downloaded to {destination_path}")
        except ClientError as e:
            print(f"Error downloading file: {e}")

# создать пустую папку
# async with self.get_client() as client:
#     await client.put_object(
#         Bucket=self.bucket_name,
#         Key="user_59/folder1/",
#         Body=b"",
#     )

# получить все объекты с индексом user_59/folder1/
# response = await client.list_objects_v2(
#     Bucket=self.bucket_name,
#     Prefix="user_59/folder1/"
# )
# получим ответ
# {
#     "Contents": [
#         {"Key": "user_59/folder1/"},
#         {"Key": "user_59/folder1/cat.jpg"},
#         {"Key": "user_59/folder1/dog.jpg"},
#         {"Key": "user_59/folder1/docs/"},
#         {"Key": "user_59/folder1/docs/report.pdf"},
#     ]
# }
# удилить их
# objects = [
#     {"Key": item["Key"]}
#     for item in response["Contents"]
# ]
# await client.delete_objects(
#     Bucket=self.bucket_name,
#     Delete={
#         "Objects": objects
#     }
# )




# async def main():
#     s3_client = S3Client(
#         access_key="",
#         secret_key="",
#         endpoint_url="",  # для Selectel используйте https://s3.storage.selcloud.ru
#         bucket_name="",
#     )
#
#     # Проверка, что мы можем загрузить, скачать и удалить файл
#     await s3_client.upload_file("test.txt")
#     await s3_client.get_file("test.txt", "text_local_file.txt")
#     await s3_client.delete_file("test.txt")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())



# Настройка клиента для Minio
# s3_client = boto3.client(
#     "s3",
#     endpoint_url="http://127.0.0.1:9000",  # Обратите внимание: 9000 - это API, 9001 - это Console (UI)
#     aws_access_key_id="minioadmin",       # Ваши креды из docker-compose
#     aws_secret_access_key="minioadmin",
#     use_ssl=False # Для локального dev, чтобы не требовало HTTPS
# )
#
# bucket_name = "user-files"
# user_id = 1
# file_name = "report.pdf"
# local_file_path = "/path/to/report.pdf"
#
# # Формируем "путь" (префикс). Это просто строка.
# s3_key = f"user_{user_id}/{file_name}"
#
# # Загружаем файл. Папка user_1 создастся неявно.
# s3_client.upload_file(
#     Filename=local_file_path,
#     Bucket=bucket_name,
#     Key=s3_key,
#     ExtraArgs={"ContentType": "application/pdf"} # Важно для корректного отображения
# )
#
# print(f"Файл загружен по ключу: {s3_key}")