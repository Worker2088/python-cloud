"""
Модуль конфигурации приложения.

Назначение:
- загрузка конфигурации из env
- хранение настроек БД, JWT, Redis, MinIO
- формирование вспомогательных computed properties
"""

import logging
from typing import ClassVar

from pydantic import computed_field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class AuthSettings(BaseModel):
    """
    Настройки авторизации.

    Attributes:
        secret: секретный ключ JWT
        expire_minutes: время жизни токена
    """

    secret: str
    expire_minutes: int


class Settings(BaseSettings):
    """
    Основной конфиг приложения.

    Загружается из .env файла.

    Содержит:
    - настройки PostgreSQL
    - настройки Redis
    - JWT конфигурацию
    - MinIO конфигурацию
    - режим debug
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    postgres_user: str = ""
    postgres_password: str = ""
    postgres_host: str = ""
    postgres_port: str = ""  # postgres_port: int = ""
    postgres_db: str = ""

    # debug: bool = False
    debug: bool = True # для разработки


    jwt_secret: str = ""
    jwt_expire_minutes: str = ""  # время жизни JWT токена # jwt_expire_minutes: int = ""  # время жизни JWT токена

    # redis_url: str = "redis://redis:6379"
    redis_url: str = "redis://localhost:6379" # для разработки

    # TTL сессии. Явно указываем, что это переменная класса, а не поле модели, чтобы избежать валидации Pydantic
    TTL: ClassVar[int] = 86400

    minio_root_user: str = ""
    minio_root_password: str = ""
    minio_endpoint: str = ""
    minio_bucket_name: str = ""

    # @computed_field
    @property
    def db_url(self) -> str:
        """
        Формирует async SQLAlchemy database URL.

        Returns:
            str: строка подключения к PostgreSQL
        """
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )

    @property
    def auth(self) -> AuthSettings:
        """
        Возвращает объект настроек авторизации.

        Returns:
            AuthSettings: JWT конфигурация
        """
        return AuthSettings(
            secret=self.jwt_secret, expire_minutes=int(self.jwt_expire_minutes)
        )
