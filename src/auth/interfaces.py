"""
Контракт репозитория пользователей для абстракции работы с БД
"""

from typing import Protocol
from src.auth.models import User


class IUserRepository(Protocol):
    """
    Интерфейс репозитория пользователей.
    """

    async def create_user(self, username: str, hashed_password: str) -> User:
        """Создаёт пользователя в БД."""
        ...

    async def authenticate(self, username: str, hashed_password: str) -> User:
        """Аутентификация пользователя."""
        ...

    async def get_user_by_name(self, user_name: str) -> User:
        """Получение пользователя по username."""
        ...

    async def get_user_by_id(self, user_id: int) -> User:
        """Получение пользователя по ID."""
        ...
