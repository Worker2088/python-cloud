from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.interfaces import IUserRepository
from src.auth.repository import UserRepository
from src.auth.service import UserService
from src.db.database import get_session


# alias для DI или "алиас зависимости"
DBSessionDepends = Annotated[AsyncSession, Depends(get_session)]

# собираем матрешку для нашего роутера auth
# Зависимость для создания репозитория
def get_user_repository(session: DBSessionDepends) -> IUserRepository:
    return UserRepository(session)

# Зависимость для создания сервиса, которая сама затребует репозиторий
def get_user_service(repo: IUserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

# Удобный алиас для аннотации в роутере
UserServiceDepends = Annotated[UserService, Depends(get_user_service)]