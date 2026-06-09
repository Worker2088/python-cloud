import logging
from typing import Optional

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, HTTPException, Response, Query, status

from src.auth.dependencies import CurrentUserDeps
from src.auth.exception import UserAlreadyExistsError, UserNotLoggedInError, UserNotFoundError, DatabaseError
from src.auth.models import User
from src.auth.schemas import UserRegisterRequest, JWTResponse, UserLoginRequest, SessionResponse, UserResponse
from src.auth.service import UserService
from src.storage.exception import FolderAlreadyExistsError, ForbiddenError, FolderDeleteError, FolderNotFoundError
from src.storage.schemas import CreateFolderRequest, CreateFolderResponse, DeleteFolderRequest
from src.storage.service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/directory/", response_model=CreateFolderResponse)
@inject
async def create_folder(
        create_folder_dto: CreateFolderRequest,
        storage_service: FromDishka[StorageService],
        current_user: CurrentUserDeps,
        # response: Response
        ):
    logger.debug("!!!начал создание новой папки, %s", create_folder_dto.name)

    create_folder_response = await storage_service.create_folder(create_folder_dto, current_user.id)

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







