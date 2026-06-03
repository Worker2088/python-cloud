import logging
import uuid

import redis.asyncio as redis

logger = logging.getLogger(__name__)

class ISessionStorage:
    async def create_session(self, user_id: int) -> str: ...
    async def get_user_id(self, session_id: str) -> int | None: ...
    async def delete_session(self, session_id: str) -> None: ...


class RedisSessionStorage(ISessionStorage):
    def __init__(self, redis: redis.Redis):
        self.redis = redis

    async def create_session(self, user_id: int) -> str:
        session_id = str(uuid.uuid4())
        logger.debug("!!!session_id, %s", session_id)

        await self.redis.set(
            session_id,
            str(user_id),
            ex=60 * 60 * 24  # 24h TTL
        )

        return session_id

    async def get_user_id(self, session_id: str) -> int | None:
        user_id = await self.redis.get(session_id)
        logger.debug("!!!user_id, %s", user_id)

        if user_id is None:
            return None
        return int(user_id)

    async def delete_session(self, session_id: str) -> None:
        await self.redis.delete(session_id)