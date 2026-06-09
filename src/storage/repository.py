import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exception import UserAlreadyExistsError, DatabaseError
from src.auth.models import User
from src.storage.exception import FolderAlreadyExistsError, FolderDeleteError
from src.storage.models import Folder

logger = logging.getLogger(__name__)


class StorageRepository():
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_folder(self, user_id: int, name: str, parent_id: int) -> Folder:
        folder = Folder(user_id=user_id, name=name, parent_id=parent_id)

        self.session.add(folder)

        # ловим ошибку уникальности - UniqueConstraint('name', 'parent_id', 'user_id', name='uq_folder_unique_name')
        try:
            await self.session.commit()
        except IntegrityError as e:
            logger.debug("имя папки не уникально, отменяю транзакцию")
            await self.session.rollback()

            if 'uq_folder_unique_name' in str(e.orig):
                logger.debug("ОШИБКА, папка с таким именем уже есть, %s", name)
                raise FolderAlreadyExistsError()
            else:
                logger.debug("ОШИБКА в БД, данные не сохранились")
                raise DatabaseError()

        await self.session.refresh(folder)
        logger.debug("новая папка создана, %s", folder)
        return folder


    async def delete_folder(self, folder: Folder) -> None:
        await self.session.delete(folder)
        await self.session.commit()


    async def get_folder_by_id(self, folder_id: int) -> Folder | None:
        logger.debug("folder_id, %s", folder_id)

        stmt = select(Folder).where(Folder.id == folder_id)

        result = await self.session.execute(stmt)
        logger.debug("result, %s", result)
        folder = result.scalar_one_or_none()

        return folder








        # удаление
        # await self.session.delete(user)
        # await self.session.commit()
        # апдейт
        # user = await self.session.get(User, user_id)
        # user.username = new_username
        # await self.session.commit()
        # await self.session.refresh(user)
