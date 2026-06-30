"""
Pydantic схемы для API.

Используются для:
- валидации входных данных
- сериализации ответов
"""

from pydantic import BaseModel, Field, ConfigDict


class UserRegisterRequest(BaseModel):
    """Запрос регистрации пользователя."""

    username: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    # model_config = {"extra": "allow"}
    # extra='forbid': Ошибка, если есть лишнее. (Лучший вариант для auth).
    # extra='ignore': Молча удаляем лишнее. (Допустимо, если хочешь быть мягче, но всё равно контролируешь схему)
    # extra='allow': Сохраняем лишнее в model_extra. (Почти никогда не нужно в auth)

class UserLoginRequest(BaseModel):
    """Запрос логина пользователя."""

    username: str = Field(min_length=5, max_length=100)
    password: str = Field(min_length=8, max_length=100)


class JWTResponse(BaseModel):
    """Ответ с JWT токеном."""

    token: str
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Ответ с данными пользователя."""

    id: int
    username: str
    session_id: str
    model_config = ConfigDict(from_attributes=True)
