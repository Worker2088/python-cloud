"""
Тесты модуля аутентификации.

Проверяют:
- регистрацию пользователя
- обработку дублей username
- интеграцию router → service → DB → DI
"""

import logging

import pytest

from src.core.middleware.logging import logger


logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_example():
    """
    Базовый smoke test.
    Проверяет что тестовая инфраструктура работает.
    """
    assert 1 == 1


@pytest.mark.asyncio
async def test_successful_sign_up(async_client):
    """
    Проверка успешной регистрации пользователя.

    Flow теста:
    router → service → repo → DB → session storage → response
    """

    user_data = {"username": "test_user_1", "password": "strong_password_123"}

    response = await async_client.post("/api/auth/sign-up", json=user_data)

    assert response.status_code == 200

    data = response.json()

    assert "session_id" in data
    assert isinstance(data["session_id"], str)


async def test_duplicate_username_sign_up(async_client):
    """
    Проверка защиты от создания дубликатов пользователей.

    Ожидаем:
    - первый запрос успешный
    - второй возвращает 409 Conflict
    """

    user_data = {"username": "unique_user", "password": "password"}

    await async_client.post("/api/auth/sign-up", json=user_data)

    response = await async_client.post("/api/auth/sign-up", json=user_data)
    logger.debug("!!!response.status_code, %s", response.status_code)
    logger.debug("!!!response.json(), %s", response.json())

    assert response.status_code == 409
