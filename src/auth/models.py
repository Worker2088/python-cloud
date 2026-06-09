

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class User(Base):
    """
    Модель пользователя.
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(length=50), unique=True,
        nullable=False,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default= True, index=True)

    # access_key: Mapped[str] = mapped_column(
    #         String(length=1024), unique=True,
    #         nullable=False)
    # secret_key: Mapped[str] = mapped_column(
    #         String(length=1024), unique=True,
    #         nullable=False)
    # endpoint_url: Mapped[str] = mapped_column(
    #             String(length=1024),
    #             nullable=False)
    # bucket_name: Mapped[str] = mapped_column(
    #             String(length=1024),
    #             nullable=False)

    # имя
    # размер
    # владелец
    # путь