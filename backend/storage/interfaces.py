"""
Модуль интерфейса репозитория хранилища.

Определяет контракт (Protocol) для работы с S3-подобным хранилищем.
Используется для DI и подмены реализации (S3, mock, local storage).
"""

from typing import Protocol


class IStorageRepository(Protocol):
    """
    Интерфейс слоя доступа к объектному хранилищу.
    """

    async def put_object(self, key: str, body: bytes = b"") -> str:
        """Создать объект в хранилище."""

    async def copy_object(self, from_key: str, to_key: str) -> str:
        """Скопировать объект внутри хранилища."""

    async def get_list_objects_with_delimiter(self, key: str) -> dict:
        """Получить список объектов с разделением на файлы и папки."""

    async def get_list_objects(self, key: str) -> list[dict]:
        """Получить плоский список объектов по префиксу."""

    async def size_file(self, s3_key: str) -> int:
        """Получить размер файла."""

    async def delete_object(self, s3_key: str) -> None:
        """Удалить один объект."""

    async def delete_list_objects(self, s3_key: str) -> None:
        """Удалить список объектов (папку рекурсивно)."""

    async def object_exists(self, key: str) -> bool:
        """Проверить существование объекта."""

    async def get_info_objects(self, s3_key: str) -> dict:
        """Получить метаданные объекта."""

    async def get_object(self, key: str) -> bytes:
        """Получить содержимое объекта."""
