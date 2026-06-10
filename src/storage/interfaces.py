from typing import Protocol

from src.storage.models import Folder


class IStorageRepository(Protocol):

    async def create_folder(self, user_id: int, name: str, parent_id: int) -> Folder:
        ...

    async def delete_folder(self, folder_id: int) -> None:
        ...

    async def get_folder_by_id(self, folder_id: int) -> Folder | None:
        ...

    async def get_folder_id_by_path(self, user_id: int, path: str) -> int | None:
        pass
