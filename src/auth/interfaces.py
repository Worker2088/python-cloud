from typing import Protocol

from src.auth.models import User


class IUserRepository(Protocol):

    async def create_user(self, username: str, hashed_password: str) -> User:
        ...

    async def authenticate(self, username: str, hashed_password: str) -> User:
        ...

    async def get_user_by_name(self, user_name: str) -> User:
        ...

    async def get_user_by_id(self, user_id: int) -> User:
        ...
