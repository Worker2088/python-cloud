import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User


logger = logging.getLogger(__name__)


class UserRepository():
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_user(self, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)
        logger.debug("user, %s", user)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.debug("new user, %s", user)

        return user

