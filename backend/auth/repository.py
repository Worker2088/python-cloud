"""
Репозиторий пользователей.

Отвечает за:
- работу с БД (SQLAlchemy)
- CRUD операции User
- обработку ошибок БД
"""

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.exception import UserAlreadyExistsError, DatabaseError
from backend.auth.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Реализация IUserRepository через SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, username: str, hashed_password: str) -> User:
        """Создание пользователя в БД."""
        user = User(username=username, hashed_password=hashed_password)

        self.session.add(user)

        # тк поле username у нас unique=True, то ловим ошибку в репо
        try:
            await self.session.commit()
        except IntegrityError as e:
            logger.info(
                "!!!ОШИБКА, юзер с таким именем уже есть в БД, %s, %s", e.code, e.detail
            )

            await self.session.rollback()

            # ловим нужную нам ошибку UNIQUE violation - ошибка уникальности поля, ее код 23505
            if getattr(e.orig, "sqlstate", None) == "23505":
                raise UserAlreadyExistsError()
            else:
                # ловим все остальные ошибки БД, чтобы прил не упало
                raise DatabaseError()

        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Получение пользователя по ID."""

        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        return user

    async def get_user_by_name(self, user_name: str) -> User | None:
        """Получение пользователя по username."""

        result = await self.session.execute(
            select(User).where(User.username == user_name)
        )
        user = result.scalar_one_or_none()

        return user
