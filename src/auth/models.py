"""
ORM модель пользователя.

Представляет таблицу users в БД.
"""

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class User(Base):
    """
    Модель пользователя системы.

    Attributes:
        id: PK
        username: уникальное имя пользователя
        hashed_password: хэш пароля
        is_active: статус активности аккаунта
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    username: Mapped[str] = mapped_column(
        String(length=50), unique=True, nullable=False, index=True
    )

    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
