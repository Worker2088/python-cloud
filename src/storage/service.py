import logging

from fastapi import UploadFile

from src.auth.session.storage import ISessionStorage
from src.storage.exception import ForbiddenError, FolderNotFoundError
from src.storage.interfaces import IStorageRepository
from src.storage.models import Folder
from src.storage.s3 import S3Client
from src.storage.schemas import CreateFolderRequest, CreateFolderResponse, DeleteFolderRequest, StorageObjectSchema, \
    ObjectType

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self,
                 repo: IStorageRepository,
                 session: ISessionStorage,
                 s3_client: S3Client,
                ):
        self.repo = repo
        self.session = session
        self.s3_client = s3_client

    async def create_folder(self, path: str, current_user_id: int) -> CreateFolderResponse:

        folder_name, parent_parts = self.split_path_into_name_and_parent(path)

        parent_id = None

        if parent_parts:
            parent_id = await self.repo.get_folder_id_by_path(
                user_id=current_user_id,
                parts=parent_parts
            )

        # 5. создаём папку
        new_folder = await self.repo.create_folder(
            user_id=current_user_id,
            name=folder_name,
            parent_id=parent_id
        )
        logger.debug("!!!новая папка создана, id, %s", new_folder.id)
        logger.debug("!!!new_folder, %s", new_folder.name)

        result = '/'.join(parent_parts) + '/'
        logger.debug("!!!result, %s", result)

        # 6. собираем path для ответа
        # response_path = self.build_parent_path(new_folder)
        response_path = result
        # logger.debug("!!!вычисляю путь - self.build_parent_path(response_path), %s", response_path)

        return CreateFolderResponse(
            path=response_path,
            name=new_folder.name,
            type="DIRECTORY",
        )


    # async def build_parent_path(self, folder: Folder) -> str:
    #     parts = []
    #
    #     current = await self.repo.get_folder_by_id(folder.parent_id)
    #     logger.debug("!!!current, %s", current)
    #
    #     while current is not None:
    #         parts.append(current.name)
    #
    #         current = await self.repo.get_folder_by_id(current.parent_id)
    #         logger.debug("!!!current, %s", current)
    #
    #     parts.reverse()
    #
    #     return "/".join(parts) + "/" if parts else ""


    async def delete_folder(self, folder_id: int, current_user_id: int) -> None:

        folder = await self.repo.get_folder_by_id(folder_id)
        logger.debug("!!!удаляю папку, %s", folder)

        if folder is None:
            raise FolderNotFoundError()

        if folder.user_id != current_user_id:
            raise ForbiddenError()

        await self.repo.delete_folder(folder)
        logger.debug("!!!удалена папка, %s", folder.name)


    async def info_folder(self, path: str, current_user_id: int) -> list[StorageObjectSchema] | None:

        folder_name, parent_parts = self.split_path_into_name_and_parent(path)
        parent_parts.append(folder_name)

        folder_id = await self.repo.get_folder_id_by_path(
            user_id=current_user_id,
            parts=parent_parts
        )
        logger.debug("!!!folder_id, %s", folder_id)

        folder = await self.repo.get_folder_by_id(folder_id)
        logger.debug("!!!folder, %s", folder)

        if folder.user_id != current_user_id:
            logger.debug("!!!folder.user_id != current_user_id, %s", folder.user_id != current_user_id)
            raise ForbiddenError()

        # list_folder = await self.repo.get_info_folder_by_id(folder_id, )
        list_children = folder.children
        logger.debug("!!!list_children, %s", list_children)

        result_dto: list[StorageObjectSchema] = []

        for children in list_children:
            dto = StorageObjectSchema(
                path=path,
                name=children.name,
                type=ObjectType.DIRECTORY,  # Это папка
                size=None  # У папок обычно нет размера (или считаем рекурсивно)
            )
            logger.debug("!!!dto, %s", dto)

            result_dto.append(dto)

        logger.debug("!!!result_dto, %s", result_dto)
        return result_dto


    async def upload_file(self, path: str, current_user_id: int, uploaded_files: list[UploadFile]) -> StorageObjectSchema:
        for uploaded_file in uploaded_files:
            file = uploaded_file.file
            file_name = uploaded_file.filename
            size = uploaded_file.size

            # формирую ключ
            # s3_key = f"user_{user_id}/{file.filename}"

            with open(f"{file_name}", "wb") as f:
                f.write(file.read())

            # Загружаем в S3
            # await self.s3_client.upload_file(
            #     file=file,
            #     object_name=s3_key,
            # )

        results = []

        # contents = await uploaded_file.read()
        # size = len(contents)

        # if folder.user_id != current_user_id:
        #     raise ForbiddenError()

        # --- ЗДЕСЬ ВАША ЛОГИКА ЗАГРУЗКИ В S3 / ДИСК ---
        # s3_client.put_object(Bucket=..., Key=..., Body=contents)
        # Или сохранение в БД (создание записи Folder/File)
        # ---------------------------------------------

        results.append({
            # "path": f"{final_path}/" if final_path else "", # ТЗ требует слэш в конце пути
            "path": path,
            "name": file_name,
            "size": size,
            "type": "FILE"
        })
        return results



    def split_path_into_name_and_parent(self, path: str):
        # 1. чистим путь
        clean_path = path.strip("/")
        logger.debug("!!!чистим путь clean_path, %s", clean_path)

        # 2. разбиваем
        parts = clean_path.split("/")
        logger.debug("!!!разбиваем parts, %s", parts)

        # 3. имя последнего элемента (папки)
        folder_name = parts[-1]
        logger.debug("!!!имя новой папки, %s", folder_name)

        # 4. путь до последнего элемента
        parent_parts = parts[:-1]
        logger.debug("!!!путь до родителя, %s", parent_parts)

        return folder_name, parent_parts