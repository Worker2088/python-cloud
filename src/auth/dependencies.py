import logging
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import HTTPException, Depends, Cookie
from fastapi.security import OAuth2PasswordBearer

from src.auth.jwt import IJWT, JWT
from src.auth.models import User
from src.auth.service import UserService
from src.auth.session.storage import ISessionStorage

logger = logging.getLogger(__name__)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")

# --------------------------------------------
# реализация через сессии

@inject
async def get_current_user(
        sessions: FromDishka[ISessionStorage],
        service: FromDishka[UserService],
        session_id: str | None = Cookie(default=None),
) -> User:

    if not session_id:
        raise HTTPException(401, "No session")

    user_id = await sessions.get_user_id(session_id)
    logger.debug("!!!sessions.get_user_id(session_id), user_id %s", user_id)

    if not user_id:
        raise HTTPException(401, "Invalid session")

    return await service.get_user_by_id(user_id)

CurrentUserDeps = Annotated[User, Depends(get_current_user)]

# --------------------------------------------
# реализация через JWT

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")

# @inject
# async def get_current_user(
#         token: Annotated[str, Depends(oauth2_scheme)],
#         service: FromDishka[UserService],
#         jwt: FromDishka[IJWT]
# ) -> User:
#     logger.debug("TOKEN RAW: %s", token)
#     user_id = jwt.decode_access_token(token)
#     logger.debug("user_id: %s", user_id)
#
#     if user_id is None:
#         raise HTTPException(401, "Invalid token")
#     logger.debug("!!!jwt.decode_access_token(token), user_id %s", user_id)
#
#     user = await service.get_user_by_id(user_id)
#
#     if user is None:
#         raise HTTPException(401, "User not found")
#     logger.debug("!!!service.get_user_by_id(user_id), username %s", user.username)
#
#     return user
#
# CurrentUserDeps = Annotated[User, Depends(get_current_user)]


# alias для DI или "алиас зависимости"
# DBSessionDepends = Annotated[AsyncSession, Depends(get_session)]
#
# # собираем матрешку для нашего роутера auth
# # Зависимость для создания репозитория
# def get_user_repository(session: DBSessionDepends) -> IUserRepository:
#     return UserRepository(session)
#
# # Зависимость для создания сервиса, которая сама затребует репозиторий
# def get_user_service(repo: IUserRepository = Depends(get_user_repository)) -> UserService:
#     return UserService(repo)
#
# # Удобный алиас для аннотации в роутере
# UserServiceDepends = Annotated[UserService, Depends(get_user_service)]


