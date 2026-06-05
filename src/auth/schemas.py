from pydantic import BaseModel, Field, ConfigDict


class UserRegisterRequest(BaseModel):

    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=100)

    model_config = {"extra": "allow"}


# class UserRegisterResponse(BaseModel):
#     username: str
#
#     # Включаем поддержку ORM-моделей
#     model_config = ConfigDict(from_attributes=True, extra="allow")


class UserLoginRequest(BaseModel):

    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=100)

    model_config = {"extra": "allow"}

# используется если авторизация через jwt
class JWTResponse(BaseModel):
    token: str

    # Включаем поддержку ORM-моделей
    model_config = ConfigDict(from_attributes=True, extra="allow")

# используется если авторизация через сессии
class SessionResponse(BaseModel):
    id: int
    username: str
    session_id: str
    # Включаем поддержку ORM-моделей
    model_config = ConfigDict(from_attributes=True, extra="allow")

class UserResponse(BaseModel):
    id: int
    username: str
    session_id: str
    # Включаем поддержку ORM-моделей
    model_config = ConfigDict(from_attributes=True, extra="allow")