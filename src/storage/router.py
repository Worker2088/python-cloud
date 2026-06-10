import logging
import mimetypes
from typing import Optional

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, HTTPException, Response, Query, status, UploadFile, File

# StreamingResponse библиотека для передачи файлов по запросу которые хранятся в удаленной БД (S3)
# FileResponse для передачи локальных файлов
from fastapi.responses import StreamingResponse, FileResponse

from src.auth.dependencies import CurrentUserDeps
from src.auth.exception import UserAlreadyExistsError, UserNotLoggedInError, UserNotFoundError, DatabaseError
from src.auth.models import User
from src.auth.schemas import UserRegisterRequest, JWTResponse, UserLoginRequest, SessionResponse, UserResponse
from src.auth.service import UserService
from src.storage.exception import FolderAlreadyExistsError, ForbiddenError, FolderDeleteError, FolderNotFoundError
from src.storage.schemas import CreateFolderRequest, CreateFolderResponse, DeleteFolderRequest, StorageObjectSchema
from src.storage.service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/directory", response_model=CreateFolderResponse)
# http://localhost:8000/api/directory?path=folder_1/folder_2/folder_3/
# где имя создаваемой папки, folder_1/folder_2 путь к этой папки
# те последнее всегда имя создаваемой папки
# если путь # http://localhost:8000/api/directory?path=folder_1/
# то папка создается в корне
@inject
async def create_folder(
        # create_folder_dto: CreateFolderRequest,
        storage_service: FromDishka[StorageService],
        current_user: CurrentUserDeps,
        path: str | None = Query(default=None),
        # response: Response
        ):
    logger.debug("!!!path, %s", path)
    logger.debug("!!!начал создание новой папки, %s", path)

    create_folder_response = await storage_service.create_folder(path, current_user.id)

    return create_folder_response


@router.delete("/resource/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_folder(
        folder_id: int,
        storage_service: FromDishka[StorageService],
        current_user: CurrentUserDeps,
        ):
    logger.debug("!!!начал удаление папки, %s", folder_id)

    await storage_service.delete_folder(folder_id, current_user.id)


@router.get("/directory", response_model=list[StorageObjectSchema])
@inject
async def info_folder(
        storage_service: FromDishka[StorageService],
        current_user: CurrentUserDeps,
        path: str | None = Query(default=None),
        # response: Response
        ):
    logger.debug("!!!получаю инфо о содержимом папки (путь), %s", path)

    info_folder_response = await storage_service.info_folder(path, current_user.id)

    return info_folder_response

# ручка для загрузки файлов
@router.post("/resource", response_model=list[StorageObjectSchema])
@inject
async def upload_file(
        storage_service: FromDishka[StorageService],
        current_user: CurrentUserDeps,
        path: str | None = Query(default=None),
        uploaded_files: list[UploadFile] = File(...),
):

    results = await storage_service.upload_file(path, current_user.id, uploaded_files)

    return results


# ручка для получения локального файла
@router.get("/resource/{file_name}")
@inject
async def get_local_file(file_name: str):
    return FileResponse(file_name)


# генератор, чтобы отдавать большие файлы чанками
def iterfile(file_name: str):
    with open(file_name, "rb") as file:
        while chunk := file.read(1024 * 1024):
            yield chunk


# ручка для получения файла из S3
@router.get("/resource_s3/{file_name}")
@inject
async def get_s3_file(file_name: str): # media_type определяем по расширению файла
    return StreamingResponse(iterfile(file_name), media_type= get_media_type(file_name))


# функция определения media_type через встроенный модуль mimetypes
def get_media_type(file_name: str) -> str:
    # mimetypes.guess_type возвращает кортеж (type, encoding)
    mime_type, _ = mimetypes.guess_type(file_name)

    # Если тип не найден, возвращаем бинарный по умолчанию
    return mime_type or "application/octet-stream"