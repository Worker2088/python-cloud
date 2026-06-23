"""
Модуль получения текущего пользователя.

Отвечает за:
- извлечение session_id из cookie
- получение user_id из Redis
- загрузку пользователя из БД
- установку user_id в request context (ContextVar)
"""

import logging
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer

from src.auth.models import User
from src.auth.service import UserService
from src.auth.session.storage import ISessionStorage
from src.core.request_context import user_id_ctx_var
from src.storage.exception import UnauthorizedError

logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")


@inject
async def get_current_user(
    sessions: FromDishka[ISessionStorage],
    service: FromDishka[UserService],
    session_id: str | None = Cookie(default=None),
) -> User:
    """
    Dependency для получения текущего авторизованного пользователя.

    Flow:
    1. Берём session_id из cookie
    2. Достаём user_id из Redis
    3. Загружаем User из БД
    4. Сохраняем user_id в ContextVar (для логирования)

    Raises:
        UnauthorizedError: если сессия отсутствует или невалидна

    Returns:
        User: текущий пользователь
    """

    if not session_id:
        raise UnauthorizedError()

    user_id = await sessions.get_user_id(session_id)

    if not user_id:
        raise UnauthorizedError()

    # Контекстная переменная с user_id (ContextVar)
    user_id_ctx_var.set(str(user_id))

    return await service.get_user_by_id(user_id)


CurrentUserDeps = Annotated[User, Depends(get_current_user)]


# --------------------------------------------
# реализация через JWT

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")

# @inject
# async def get_current_user(
#         token: Annotated[str, Depends(oauth2_scheme)],
#         service: FromDishka[UserService],
#         jwt: FromDishka[IJWT]
# ) -> User:
#     logger.debug("TOKEN RAW: %s", token)
#     user_id = jwt.decode_access_token(token)
#     logger.debug("user_id: %s", user_id)
#
#     if user_id is None:
#         raise HTTPException(401, "Invalid token")
#     logger.debug("!!!jwt.decode_access_token(token), user_id %s", user_id)
#
#     user = await service.get_user_by_id(user_id)
#
#     if user is None:
#         raise HTTPException(401, "User not found")
#     logger.debug("!!!service.get_user_by_id(user_id), username %s", user.username)
#
#     user_id_ctx_var.set(str(user_id))
#
#     return user
#
# CurrentUserDeps = Annotated[User, Depends(get_current_user)]
