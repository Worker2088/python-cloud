"""
Модуль API-роутера для работы с файловым хранилищем (S3-подобное хранилище).

Содержит HTTP endpoints для:
- создания папок
- загрузки файлов
- удаления объектов
- перемещения объектов
- получения информации о файлах/папках
- поиска
- скачивания файлов и папок (в виде ZIP)

Все операции выполняются в контексте текущего пользователя.
"""

import io
import logging

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query, status, UploadFile, File

from fastapi.responses import StreamingResponse

from src.auth.dependencies import CurrentUserDeps
from src.storage.schemas import StorageObjectSchema, DownloadResultDTO
from src.storage.service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/directory", response_model=StorageObjectSchema)
@inject
async def create_folder(
    storage_service: FromDishka[StorageService],
    current_user: CurrentUserDeps,
    path: str = Query(...),
):
    """
    Создание пустой папки в хранилище пользователя.

    Args:
        storage_service: сервис работы с хранилищем
        current_user: текущий авторизованный пользователь
        path: путь создаваемой папки

    Returns:
        StorageObjectSchema: информация о созданной папке
    """

    create_folder_response = await storage_service.create_folder(path, current_user.id)

    return create_folder_response


@router.post("/resource", response_model=list[StorageObjectSchema])
@inject
async def upload_object(
    storage_service: FromDishka[StorageService],
    current_user: CurrentUserDeps,
    object: list[UploadFile] = File(...),
):
    """
    Загрузка одного или нескольких файлов в хранилище.

    Поддерживает загрузку папок (через относительные пути в filename).

    Args:
        storage_service: сервис хранилища
        current_user: текущий пользователь
        object: список файлов UploadFile

    Returns:
        list[StorageObjectSchema]: список загруженных объектов
    """

    uploaded_objects = []

    for file in object:
        file_bytes = await file.read()

        original_filename = file.filename
        logger.info("!!!original_filename, %s", original_filename)

        if not original_filename:
            continue

        full_path = original_filename

        result = await storage_service.create_object(
            full_path, current_user.id, file_bytes
        )
        uploaded_objects.extend(result)

    return uploaded_objects


@router.delete("/resource", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_object(
    storage_service: FromDishka[StorageService],
    current_user: CurrentUserDeps,
    path: str = Query(...),
):
    """
    Удаление файла или папки.

    Args:
        storage_service: сервис хранилища
        current_user: текущий пользователь
        path: путь объекта

    Returns:
        None
    """

    return await storage_service.delete_object(path, current_user.id)


@router.get("/resource/move", response_model=StorageObjectSchema)
@inject
async def move_object(
    storage_service: FromDishka[StorageService],
    current_user: CurrentUserDeps,
    from_path: str = Query(..., alias="from"),
    to_path: str = Query(..., alias="to"),
):
    """
    Перемещение или переименование файла/папки.

    Args:
        storage_service: сервис хранилища
        current_user: текущий пользователь
        from_path: исходный путь
        to_path: целевой путь

    Returns:
        StorageObjectSchema: информация о перемещённом объекте
    """

    move_object_response = await storage_service.move_object(
        from_path, to_path, current_user.id
    )

    return move_object_response


# TODO переделать
@router.get("/resource", response_model=StorageObjectSchema)
@inject
async def info_object(
    storage_service: FromDishka[StorageService],
    current_user: CurrentUserDeps,
    path: str = Query(...),
):
    """
    Получение информации об одном объекте (файл или папка).

    Args:
        storage_service: сервис хранилища
        current_user: текущий пользователь
        path: путь объекта

    Returns:
        StorageObjectSchema: информация об объекте
    """

    info_object_response = await storage_service.get_info_object(path, current_user.id)

    return info_object_response


@router.get("/directory", response_model=list[StorageObjectSchema])
@inject
async def get_info_object(
    storage_service: FromDishka[StorageService],
    current_user: CurrentUserDeps,
    path: str = Query(...),
):
    """
    Получение содержимого папки.

    Args:
        storage_service: сервис хранилища
        current_user: текущий пользователь
        path: путь папки

    Returns:
        list[StorageObjectSchema]: список файлов и папок
    """

    info_objects_response = await storage_service.get_info_object(path, current_user.id)

    return info_objects_response


@router.get("/resource/search", response_model=list[StorageObjectSchema])
@inject
async def search_object(
    storage_service: FromDishka[StorageService],
    current_user: CurrentUserDeps,
    query: str = Query(...),
):
    """
    Поиск файлов и папок по имени или пути.

    Args:
        storage_service: сервис хранилища
        current_user: текущий пользователь
        query: поисковый запрос

    Returns:
        list[StorageObjectSchema]: найденные объекты
    """
    search_objects_response = await storage_service.search_objects(
        current_user.id, query
    )

    return search_objects_response


@router.get("/resource/download", response_model=DownloadResultDTO)
@inject
async def download_object(
    storage_service: FromDishka[StorageService],
    current_user: CurrentUserDeps,
    path: str = Query(...),
):
    """
    Скачивание файла или папки.

    Если это папка — возвращается ZIP-архив.

    Args:
        storage_service: сервис хранилища
        current_user: текущий пользователь
        path: путь объекта

    Returns:
        StreamingResponse: поток файла или ZIP-архива
    """

    result = await storage_service.download_object(current_user.id, path)

    stream = io.BytesIO(result.content)

    return StreamingResponse(
        stream,
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )
