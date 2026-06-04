import logging

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, HTTPException

from src.auth.dependencies import CurrentUserDeps
from src.auth.exception import UserAlreadyExists, UserNotLogin, UserNotFound
from src.auth.models import User
from src.auth.schemas import UserRegisterRequest, JWTResponse, UserLoginRequest, SessionResponse
from src.auth.service import UserService
# from src.auth.session.service import SessionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth") # создай mini-app для группы роутов
# router это папка/контейнер с группой endpoint'ов


# --------------------------------------------
# реализация через сессии

@router.post("/sign-up", response_model=SessionResponse)
@inject  # <-- ОБЯЗАТЕЛЬНО: этот декоратор заставляет Dishka искать маркеры в аргументах
async def create_user(
        create_user_dto: UserRegisterRequest,
        user_service: FromDishka[UserService]
        ):
    logger.debug("!!!начал регистрацию нового юзера, %s", create_user_dto)

    try:
        session_id = await user_service.create(create_user_dto)
        return SessionResponse(session_id=session_id)

    except UserAlreadyExists:
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )


@router.post("/sign-in", response_model=SessionResponse)
@inject
async def authenticate(
        user: UserLoginRequest,
        user_service: FromDishka[UserService]
        ):
    logger.debug("!!!начал авторизацию нового юзера, %s", user)

    try:

        session_id = await user_service.authenticate(user)
        return SessionResponse(session_id=session_id)

    except UserNotLogin:
        raise HTTPException(
            status_code=409,
            detail="user is not registered"
        )
    except UserNotFound:
        raise HTTPException(
            status_code=404,
            detail="user not found"
        )


@router.get("/me")
@inject
# async def me(current_user: FromDishka[User]):
async def me(current_user: CurrentUserDeps):
    return {
        "id": current_user.id,
        "username": current_user.username,
    }


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


# --------------------------------------------
# реализация через JWT

# @router.post("/sign-up", response_model=JWTResponse)
# @inject  # <-- ОБЯЗАТЕЛЬНО: этот декоратор заставляет Dishka искать маркеры в аргументах
# async def create_user(
#         create_user_dto: UserRegisterRequest,
#         user_service: FromDishka[UserService]
#         ):
#     logger.debug("!!!начал регистрацию нового юзера, %s", create_user_dto)
#
#     try:
#         token = await user_service.create(create_user_dto)
#         return JWTResponse(token=token)
#
#     except UserAlreadyExists:
#         raise HTTPException(
#             status_code=409,
#             detail="User already exists"
#         )
#
#
# @router.post("/sign-in", response_model=JWTResponse)
# @inject
# async def authenticate(
#         user: UserLoginRequest,
#         user_service: FromDishka[UserService]
#         ):
#     logger.debug("!!!начал авторизацию нового юзера, %s", user)
#
#     try:
#         token = await user_service.authenticate(user)
#         return JWTResponse(token=token)
#
#     except UserNotLogin:
#         raise HTTPException(
#             status_code=409,
#             detail="user is not registered"
#         )
#     except UserNotFound:
#         raise HTTPException(
#             status_code=404,
#             detail="user not found"
#         )
#
#
# @router.get("/me")
# @inject
# # async def me(current_user: FromDishka[User]):
# async def me(current_user: CurrentUserDeps):
#     return {
#         "id": current_user.id,
#         "username": current_user.username,
#     }






