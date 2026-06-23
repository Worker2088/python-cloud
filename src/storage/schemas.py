"""
Pydantic схемы storage слоя.

Используются для:
- создания папок
- отображения объектов
- ответа download
"""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class CreateFolderRequest(BaseModel):
    """DTO создания папки."""

    name: str = Field(min_length=1, max_length=100)
    path: str | None = None
    model_config = ConfigDict(from_attributes=True)


class DeleteFolderRequest(BaseModel):
    """DTO удаления папки."""

    folder_id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)


class ObjectType(str, Enum):
    """Тип объекта в storage."""

    FILE = "FILE"
    DIRECTORY = "DIRECTORY"


class StorageObjectSchema(BaseModel):
    """Единый объект storage (файл или папка)."""

    model_config = ConfigDict(use_enum_values=True)

    path: str | None = None
    name: str
    type: ObjectType
    size: int | None = None


class DownloadResultDTO(BaseModel):
    """Результат скачивания объекта."""

    content: bytes
    filename: str
    media_type: str
