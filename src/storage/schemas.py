from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class CreateFolderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    # user_id: int
    parent_id: int = None

    model_config = ConfigDict(from_attributes=True)


class CreateFolderResponse(BaseModel):
    # id: int
    name: str
    user_id: int
    parent_id: int | None = None
    # Включаем поддержку ORM-моделей
    model_config = ConfigDict(from_attributes=True)


class DeleteFolderRequest(BaseModel):
    folder_id: int
    user_id: int
    # current_user_id: int
    # parent_id: int = None

    model_config = ConfigDict(from_attributes=True)

class ObjectType(str, Enum):
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"

class StorageObjectSchema(BaseModel):
    path: str
    name: str
    type: ObjectType
    size: int | None = None