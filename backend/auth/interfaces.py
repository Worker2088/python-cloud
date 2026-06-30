"""
Контракт репозитория пользователей для абстракции работы с БД
"""

from typing import Protocol
from backend.auth.models import User


class IUserRepository(Protocol):
    """
    Интерфейс репозитория пользователей.
    """

    async def create_user(self, username: str, hashed_password: str) -> User:
        """Создаёт пользователя в БД."""
        ...

    async def get_user_by_name(self, user_name: str) -> User | None:
        """Получение пользователя по username."""
        ...

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Получение пользователя по ID."""
        ...


class ISessionStorage(Protocol):
    """
    Контракт (интерфейс) для хранения пользовательских сессий.

    Позволяет подменять реализацию (Redis, DB, memory cache).
    """

    async def create_session(self, user_id: int) -> str:
        """
        Создаёт новую сессию для пользователя.

        Returns:
            session_id (str): уникальный идентификатор сессии
        """
        ...

    async def get_user_id(self, session_id: str) -> int | None:
        """
        Получает user_id по session_id.

        Returns:
            int | None: id пользователя или None если сессия не найдена
        """
        ...

    async def delete_session(self, session_id: str) -> None:
        """
        Удаляет сессию из хранилища.
        """
        ...


class IPasswordHasher(Protocol):
    """Контракт хэшера паролей."""

    def hash_password(self, password: str) -> str:
        """Хэширование пароля."""
        ...

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля."""
        ...


class IJWT(Protocol):
    """Контракт JWT сервиса."""

    def create_access_token(self, user_id: int) -> str:
        """Создаёт JWT токен."""
        ...

    def decode_access_token(self, token: str) -> int | None:
        """Декодирует JWT и возвращает user_id."""
        ...