import logging

from pydantic import computed_field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class AuthSettings(BaseModel):
    secret: str
    expire_minutes: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str

    debug: bool = True

    jwt_secret: str
    jwt_expire_minutes: int # время жизни JWT токена
    redis_url: str = "redis://localhost:6379"

    minio_root_user: str
    minio_root_password: str
    minio_endpoint: str
    minio_bucket_name: str

    @computed_field
    @property
    def db_url(self) -> str:
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
        return AuthSettings(secret=self.jwt_secret, expire_minutes=self.jwt_expire_minutes)


# settings = Settings()
# logger.debug("создал settings %s", settings)

