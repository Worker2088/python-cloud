from pydantic import BaseModel, Field, ConfigDict

from src.auth.models import User


class UserRegistrationDTO(BaseModel):

    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=100)

    model_config = {"extra": "allow"}


class UserRegistrationDTOResponse(BaseModel):
    username: str

    # Включаем поддержку ORM-моделей
    model_config = ConfigDict(from_attributes=True, extra="allow")

