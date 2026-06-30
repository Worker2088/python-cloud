"""
Модуль управления пользовательскими сессиями.

Назначение:
- создание session_id для пользователя
- получение user_id по session_id
- удаление сессии

Используется Redis как хранилище с TTL (24 часа).
"""
from typing import Protocol
import logging
import uuid

import redis.asyncio as redis
from backend.core.settings import Settings


logger = logging.getLogger(__name__)


class RedisSessionStorage:
    """
    Реализация ISessionStorage на Redis.

    Особенности:
    - хранит session_id -> user_id
    - TTL 24 часа
    """

    def __init__(self, redis: redis.Redis):
        self.redis = redis

    async def create_session(self, user_id: int) -> str:
        """
        Создаёт сессию и сохраняет её в Redis.

        Args:
            user_id: ID пользователя

        Returns:
            session_id (str)
        """
        session_id = str(uuid.uuid4())

        await self.redis.set(
            session_id,
            str(user_id),
            ex=Settings.TTL  # 24h TTL
        )

        return session_id

    async def get_user_id(self, session_id: str) -> int | None:
        """
        Получает user_id из Redis по session_id.

        Returns:
            int | None
        """
        user_id = await self.redis.get(session_id)

        if user_id is None:
            return None
        return int(user_id)

    async def delete_session(self, session_id: str) -> None:
        """
        Удаляет session_id из Redis.
        """
        await self.redis.delete(session_id)
