from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class CreateFolderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    path: str | None = None
    #    parent_id: int = None

    model_config = ConfigDict(from_attributes=True)


class CreateFolderResponse(BaseModel):
    path: str | None = None
    name: str
    type: str

    model_config = ConfigDict(from_attributes=True)


class DeleteFolderRequest(BaseModel):
    folder_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

# схема для отображения хранимых файлов/папок
class ObjectType(str, Enum):
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"

class StorageObjectSchema(BaseModel):
    path: str
    name: str
    type: ObjectType
    size: int | None = None