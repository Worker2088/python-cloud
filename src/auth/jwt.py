import logging
from datetime import datetime, timezone, timedelta
from typing import Protocol

import jwt
from src.core.settings import Settings

logger = logging.getLogger(__name__)


class IJWT(Protocol):
    def create_access_token(self, user_id: int) -> str: ...
    def decode_access_token(self, token: str) -> int | None: ...


class JWT():
    def __init__(self, secret: str, expire_minutes: int):
        self.secret = secret
        self.expire_minutes = expire_minutes

    def create_access_token(self, user_id: int) -> str: # возвращает JWT токен
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        payload = {"sub": str(user_id), "exp": expire}
        logger.debug("!!!payload, %s", payload)
        return jwt.encode(payload, self.secret, algorithm="HS256")


    def decode_access_token(self, token: str) -> int | None: # возвращает userId
        try:
            logger.debug("DECODE TOKEN: %s", token)
            payload = jwt.decode(token, self.secret, algorithms="HS256")
            logger.debug("PAYLOAD: %s", payload)
            return int(payload["sub"])
        except (jwt.PyJWTError, ValueError, KeyError) as e:
            logger.debug("ошибка е: %s", e)
            return None