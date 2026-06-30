"""
HTTP слой (FastAPI router).

Отвечает за:
- auth endpoints
- user endpoints
- cookies (session handling)

Endpoints:
- POST /auth/sign-up
- POST /auth/sign-in
- POST /auth/sign-out
- GET  /user/me

Поддерживает session-based authentication через cookies.
"""

import logging

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Response, status, Cookie

from backend.auth.providers import CurrentUserDeps
from backend.auth.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
)
from backend.auth.service import UserService
from backend.auth.interfaces import ISessionStorage


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


# --------------------------------------------
# реализация через сессии


@router.post("/auth/sign-up", response_model=UserResponse)
@inject
async def create_user(
    create_user_dto: UserRegisterRequest,
    user_service: FromDishka[UserService],
    response: Response,
):
    """
    Регистрация нового пользователя.

    Flow:
    1. Получает данные пользователя (username, password)
    2. Вызывает UserService.create()
    3. Создаёт пользователя в БД
    4. Создаёт session_id в Redis
    5. Возвращает UserResponse
    6. Устанавливает session_id в cookie (если есть)

    Side effects:
    - создание пользователя в БД
    - создание сессии в Redis
    - установка cookie session_id
    """
    user_response = await user_service.create(create_user_dto)

    # устанавливаем куку для браузера
    response.set_cookie(
        key="session_id",
        value=str(user_response.session_id),
        httponly=True,  # Защита от кражи токена через JS-скрипты
        path="/",  # Доступно для всех эндпоинтов /api
    )
    return user_response


@router.post("/auth/sign-in", response_model=UserResponse)
@inject
async def authenticate(
    user: UserLoginRequest, user_service: FromDishka[UserService], response: Response
):
    """
    Аутентификация пользователя (login).

    Flow:
    1. Получает username/password
    2. Проверяет пользователя через UserService.authenticate()
    3. Проверяет пароль
    4. Создаёт новую session в Redis
    5. Возвращает UserResponse
    6. Устанавливает session_id в cookie

    Raises:
    - UserNotFoundError (через service layer)

    Side effects:
    - создание новой сессии
    - установка cookie session_id
    """
    user_response = await user_service.authenticate(user)

    response.set_cookie(
        key="session_id",
        value=str(user_response.session_id),
        httponly=True,
        path="/",
    )
    return user_response


@router.get("/user/me")
@inject
async def me(current_user: CurrentUserDeps):
    """
    Получение текущего авторизованного пользователя.

    Flow:
    1. Берёт user из dependency (get_current_user)
    2. Dependency проверяет session_id → Redis → DB
    3. Возвращает текущего пользователя

    Returns:
        dict: id и username текущего пользователя
    """

    return {
        "id": current_user.id,
        "username": current_user.username,
    }


@router.post("/auth/sign-out", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def logout(
    response: Response,
    sessions: FromDishka[ISessionStorage],
    session_id: str | None = Cookie(
        default=None
    ),  # Напрямую смотрим, есть ли кука session_id
):
    """
    Выход пользователя (logout).

    Flow:
    1. Берёт session_id из cookie
    2. Удаляет session из Redis
    3. Логирует факт удаления
    4. Удаляет cookie на стороне клиента

    Side effects:
    - удаление session из Redis
    - удаление cookie session_id
    """
    if session_id is not None:
        await sessions.delete_session(session_id)
        logger.info("Сессия успешно удалена из Redis, %s", session_id)

    # Даем команду браузеру немедленно уничтожить куку у себя
    response.delete_cookie(
        key="session_id",
        path="/",  # Обязательно тот же path, с которым кука создавалась!
        httponly=True,  # Желательно указывать те же флаги безопасности
    )

