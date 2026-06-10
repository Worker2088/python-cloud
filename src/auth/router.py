import logging
from typing import Optional

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, HTTPException, Response, Query, status, Cookie

from src.auth.dependencies import CurrentUserDeps
from src.auth.exception import UserAlreadyExistsError, UserNotLoggedInError, UserNotFoundError
from src.auth.models import User
from src.auth.schemas import UserRegisterRequest, JWTResponse, UserLoginRequest, SessionResponse, UserResponse
from src.auth.service import UserService
from src.auth.session.storage import ISessionStorage
from src.storage.schemas import StorageObjectSchema

# from src.auth.session.service import SessionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api") # создай mini-app для группы роутов
# router это папка/контейнер с группой endpoint'ов


# --------------------------------------------
# реализация через сессии

@router.post("/auth/sign-up", response_model=UserResponse)
@inject  # <-- ОБЯЗАТЕЛЬНО: этот декоратор заставляет Dishka искать маркеры в аргументах
async def create_user(
        create_user_dto: UserRegisterRequest,
        user_service: FromDishka[UserService],
        response: Response
        ):
    logger.debug("!!!начал регистрацию нового юзера, %s", create_user_dto)

    user_response = await user_service.create(create_user_dto)

    # 3. УСТАНАВЛИВАЕМ КУКУ ДЛЯ БРАУЗЕРА
    # Достаем session_id из ответа сервиса (проверь, как называется поле в твоем user_response)
    if hasattr(user_response, "session_id") and user_response.session_id:
        response.set_cookie(
            key="session_id",
            value=str(user_response.session_id),
            httponly=True,  # Защита от кражи токена через JS-скрипты
            path="/"  # Доступно для всех эндпоинтов /api
        )
    return user_response


@router.post("/auth/sign-in", response_model=UserResponse)
@inject
async def authenticate(
        user: UserLoginRequest,
        user_service: FromDishka[UserService],
        response: Response
        ):
    logger.debug("!!!начал авторизацию нового юзера, %s", user)

    user_response = await user_service.authenticate(user)
    # 3. УСТАНАВЛИВАЕМ КУКУ ДЛЯ БРАУЗЕРА ПРИ ЛОГИНЕ
    if hasattr(user_response, "session_id") and user_response.session_id:
        response.set_cookie(
            key="session_id",
            value=str(user_response.session_id),
            httponly=True,
            path="/"
        )
    return user_response


@router.get("/user/me")
@inject
async def me(current_user: CurrentUserDeps):
    return {
        "id": current_user.id,
        "username": current_user.username,
    }


@router.post("/auth/logout", status_code=status.HTTP_200_OK)
@inject
async def logout(
        response: Response,
        sessions: FromDishka[ISessionStorage],
        session_id: str | None = Cookie(default=None) # Напрямую смотрим, есть ли кука session_id
):
    logger.debug("!!! Начал логаут для сессии: %s", session_id)

    # 1. Если кука прилетела, стираем сессию из Redis
    if session_id:
        try:
            # Вызываем метод удаления из твоего RedisSessionStorage (например, delete_session)
            await sessions.delete_session(session_id)
            logger.debug("Сессия %s успешно удалена из Redis", session_id)
        except Exception as e:
            # Логируем ошибку, но не прерываем запрос, чтобы кука у пользователя всё равно стёрлась
            logger.error("Не удалось удалить сессию из Redis: %s", e)

    # 2. Даем команду браузеру немедленно уничтожить куку у себя
    response.delete_cookie(
        key="session_id",
        path="/",          # Обязательно тот же path, с которым кука создавалась!
        httponly=True      # Желательно указывать те же флаги безопасности
    )

    return {"detail": "Успешный выход из системы"}


# @router.get("/directory", response_model=list[StorageObjectSchema])
# @inject
# async def get_directory_contents(current_user: CurrentUserDeps, path: Optional[str] = Query("")):
#     # Здесь у вас уже есть легитимный current_user!
#     # Вы можете использовать его id, чтобы отдать файлы конкретного пользователя
#     user_id = current_user.id
#     print(f"Пользователь {current_user.username} (ID: {user_id}) запрашивает папку: '{path}'")
#
#     # Пока отдаем заглушку, но теперь безопасно
#     if path == "":
#         return [
#             {
#                 "path": "documents",
#                 "name": "Личные документы",
#                 "type": "DIRECTORY",
#                 "size": None
#             },
#             {
#                 "path": "photos",
#                 "name": "Фотографии с отпуска",
#                 "type": "DIRECTORY",
#                 "size": None
#             },
#             {
#                 "path": "important_note.txt",
#                 "name": "важная_записка.txt",
#                 "type": "FILE",
#                 "size": 4096
#             },
#             {
#                 "path": "avatar.png",
#                 "name": "avatar.png",
#                 "type": "FILE",
#                 "size": 1048576
#             }
#         ]
#
#         # Если запрашивают конкретную папку (например, кликнули на "documents")
#     return [
#         {
#             "path": f"{path}/resume.pdf",
#             "name": "Резюме_Разработчика.pdf",
#             "type": "FILE",
#             "size": 245000
#         },
#         {
#             "path": f"{path}/todo.txt",
#             "name": "список_дел.txt",
#             "type": "FILE",
#             "size": 512
#         },
#         {
#             "path": f"{path}/папка",
#             "name": "просто папка",
#             "type": "DIRECTORY",
#             "size": None
#         }
#     ]


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






