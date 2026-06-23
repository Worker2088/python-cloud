"""
Тестовая инфраструктура проекта.

Назначение:
- создание тестовой БД
- очистка данных между тестами
- создание DI контейнера для тестов
- создание HTTP клиента (AsyncClient)
"""

from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine

from dishka import make_async_container

from src.main import create_app
from src.core.settings import Settings
from src.auth.models import Base
from src.auth.providers import AdaptersProvider, InfrastructureProvider


# --------------------------------------------
# тестовые настройки окружения

test_settings = Settings(
    postgres_user="postgres",
    postgres_password="postgres",
    postgres_host="localhost",
    postgres_port=5434,
    postgres_db="test_db",
    redis_url="redis://localhost:6380",
    jwt_secret="test_secret_key_123_456_789",
    jwt_expire_minutes=60,
)

test_engine = create_async_engine(test_settings.db_url, echo=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Создаёт таблицы перед тестами и удаляет после завершения тестов.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def clear_database():
    """
    Очищает все таблицы после каждого теста.
    """
    yield

    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def app():
    """
    Создаёт FastAPI приложение с тестовым DI контейнером.
    """

    container_dishka = make_async_container(
        AdaptersProvider(), InfrastructureProvider(), context={Settings: test_settings}
    )

    fastapi_app = create_app(container_dishka=container_dishka)

    yield fastapi_app

    await container_dishka.close()


@pytest_asyncio.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP клиент для тестирования API без запуска сервера.
    """

    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
