from http.client import HTTPException
from typing import Annotated

from dishka import FromDishka
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth.models import User
from src.auth.service import UserService
from src.auth.jwt import JWT

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/sign-in")
#
# async def get_current_user(
#         token: Annotated[str, Depends(oauth2_scheme)],
#         service: FromDishka[UserService],
#         jwt: FromDishka[JWT]
# ) -> User:
#     user_id = jwt.decode_access_token(token)
#
#     if user_id is None:
#         raise HTTPException(401, "Invalid token")
#
#     user = await service.get_user_by_id(user_id)
#     if user is None:
#         raise HTTPException(401, "User not found")
#
#     return user
#
# CurrentUserDeps = Annotated[User, Depends(get_current_user)]