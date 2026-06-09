import logging

from src.auth.session.storage import ISessionStorage
from src.storage.exception import ForbiddenError, FolderNotFoundError
from src.storage.interfaces import IStorageRepository
from src.storage.schemas import CreateFolderRequest, CreateFolderResponse, DeleteFolderRequest

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self, repo: IStorageRepository, session: ISessionStorage):
        self.repo = repo
        self.session = session

    async def create_folder(self, data: CreateFolderRequest, current_user_id: int) -> CreateFolderResponse:
        logger.debug("!!!создаю папку, %s", data)

        new_folder = await self.repo.create_folder(
            user_id=current_user_id,
            name=data.name,
            parent_id=data.parent_id)
        logger.debug("!!!new_folder, %s", new_folder.name)

        return CreateFolderResponse(
            id=new_folder.id,
            name=new_folder.name,
            user_id=new_folder.user_id,
            parent_id=new_folder.parent_id
        )


    async def delete_folder(self, folder_id: int, current_user_id: int) -> None:

        folder = await self.repo.get_folder_by_id(folder_id)
        logger.debug("!!!удаляю папку, %s", folder)

        if folder is None:
            raise FolderNotFoundError()

        if folder.user_id != current_user_id:
            raise ForbiddenError()

        await self.repo.delete_folder(folder)
        logger.debug("!!!удалена папка, %s", folder.name)







