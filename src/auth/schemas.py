from pydantic import BaseModel, Field


class MyClassDTO(BaseModel):
    param1: int  # = Field(ge=0, le=100)
    param2: int  # = Field(ge=0, le=100)

    model_config = {"extra": "allow"}


class BaseUserDTO(BaseModel):
    username: str | None = Field(default=None, max_length=50)

class UserRegistrationDTO(BaseUserDTO):
    password: str = Field(min_length=8, max_length=100)

