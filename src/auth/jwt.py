"""
JWT модуль.

Назначение:
- создание access token
- декодирование токена
- извлечение user_id из payload
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Protocol

import jwt

logger = logging.getLogger(__name__)


class IJWT(Protocol):
    """Контракт JWT сервиса."""

    def create_access_token(self, user_id: int) -> str: ...

    """Создаёт JWT токен."""

    def decode_access_token(self, token: str) -> int | None: ...

    """Декодирует JWT и возвращает user_id."""


class JWT:
    """
    Реализация JWT сервиса (HS256).

    Использует:
    - secret key
    - expiration time
    """

    def __init__(self, secret: str, expire_minutes: int):
        self.secret = secret
        self.expire_minutes = expire_minutes

    def create_access_token(self, user_id: int) -> str:
        """Создание access token."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_access_token(self, token: str) -> int | None:
        """
        Декодирование JWT токена.

        Returns:
            user_id или None при ошибке
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms="HS256")
            return int(payload["sub"])
        except (jwt.PyJWTError, ValueError, KeyError):
            return None
