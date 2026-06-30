"""
Бизнес-логика пользователей.

Отвечает за:
- регистрацию
- авторизацию
- управление пользователями
- создание сессий
"""

import logging

from backend.auth.exception import UserNotFoundError
from backend.auth.interfaces import IUserRepository

# from backend.auth.jwt import IJWT
from backend.auth.models import User
from backend.auth.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
)
from backend.auth.interfaces import IPasswordHasher
from backend.auth.interfaces import ISessionStorage

logger = logging.getLogger(__name__)


# --------------------------------------------
# реализация через сессии


class UserService:
    """
    Сервис бизнес-логики пользователей.
    """

    def __init__(
        self, repo: IUserRepository, hasher: IPasswordHasher, session: ISessionStorage
    ):
        self.repo = repo
        self.hasher = hasher
        self.session = session

    async def create(self, data: UserRegisterRequest) -> UserResponse:
        """Регистрация пользователя."""

        hashed_password = self.hasher.hash_password(data.password)

        saved_user = await self.repo.create_user(
            username=data.username, hashed_password=hashed_password
        )

        session_id = await self.session.create_session(saved_user.id)

        return UserResponse(
            id=saved_user.id, username=saved_user.username, session_id=session_id
        )

    async def authenticate(self, user_dto: UserLoginRequest) -> UserResponse:
        """Авторизация пользователя."""
        user = await self.repo.get_user_by_name(user_dto.username)

        if (user is None) or (
            not self.hasher.verify_password(user_dto.password, user.hashed_password)
        ):
            logger.info("ошибка в логин/пароле, %s", user_dto.username)
            raise UserNotFoundError()

        session_id = await self.session.create_session(user.id)

        return UserResponse(id=user.id, username=user.username, session_id=session_id)

    async def get_user_by_id(self, user_id: int) -> User:
        """Получение пользователя."""

        user = await self.repo.get_user_by_id(user_id=user_id)

        if user is None:
            logger.info("юзера НЕ нашли, %s", user)
            raise UserNotFoundError()

        return user


# --------------------------------------------
# реализация через JWT

# class UserService:
#     def __init__(self, repo: IUserRepository, hasher: IPasswordHasher, jwt: IJWT):
#         self.repo = repo
#         self.hasher = hasher
#         self.jwt = jwt
#
#     async def create(self, data: UserRegisterRequest) -> str:
#         hashed_password = self.hasher.hash_password(data.password)
#
#         saved_user = await self.repo.create_user(
#             username=data.username,
#             hashed_password=hashed_password)
#
#         token = self.jwt.create_access_token(saved_user.id)
#         return token
#
#
#     async def authenticate(self, user_dto: UserLoginRequest) -> str:
#             user = await self.repo.get_user_by_name(user_dto.username)
#
#             if user is None:
#                 raise UserNotLogin()
#             if not self.hasher.verify_password(user_dto.password, user.hashed_password):
#                 raise UserNotLogin()
##
#             token = self.jwt.create_access_token(user.id)
#             return token
#
#     async def get_user_by_id(self, user_id: int) -> User:
#         user = await self.repo.get_user_by_id(user_id=user_id)
#
#         if user is None:
#             raise UserNotFound()
#
#         return user
