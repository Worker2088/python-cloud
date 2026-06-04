from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine

from dishka import make_async_container

from src.main import create_app
from src.core.settings import Settings
from src.auth.models import Base # <-- Укажи правильный импорт твоего Base
from src.auth.providers import AdaptersProvider, InfrastructureProvider, IntegrationsProvider

# 1. URL для ТЕСТОВЫХ баз. Лучше вынести в переменные окружения, но для начала пойдет так.
# TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5434/test_db"
# TEST_REDIS_URL = "redis://localhost:6380" # Тестовый Redis на другом порту

# ЯВНО переопределяем параметры для тестового окружения
test_settings = Settings(
    postgres_user = "postgres",
    postgres_password = "postgres",
    postgres_host = "localhost",
    postgres_port = 5434,
    postgres_db = "test_db",
    redis_url = "redis://localhost:6380",
    jwt_secret = "test_secret_key_123_456_789",
    jwt_expire_minutes = 60,
)

test_engine = create_async_engine(test_settings.db_url, echo=False)

# 2. Создаем таблицы перед запуском всех тестов и удаляем после
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# 3. Очищаем таблицы перед КАЖДЫМ тестом, чтобы тесты не влияли друг на друга
@pytest_asyncio.fixture(autouse=True)
async def clear_database():
    yield
    async with test_engine.begin() as conn:
        # Удали все данные из таблиц (TRUNCATE)
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

# 4. Собираем тестовое приложение с контейнером Dishka
@pytest_asyncio.fixture
async def app():
    
    # Собираем контейнер, передавая ему ТЕСТОВЫЕ настройки в контекст
    container_dishka = make_async_container(
        AdaptersProvider(),
        InfrastructureProvider(),
        IntegrationsProvider(),
        context={Settings: test_settings} 
    )
    # запускаем приложение с тестовым контейнером
    fastapi_app = create_app(container_dishka=container_dishka)

    yield fastapi_app
    
    await container_dishka.close()

# 5. Клиент для отправки HTTP-запросов
@pytest_asyncio.fixture
async def async_client(app) -> AsyncGenerator[AsyncClient, None]:
    # ASGITransport позволяет делать запросы к приложению в памяти, без запуска uvicorn
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client