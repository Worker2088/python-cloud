"""
Тесты для сервиса аутентификации.
Проверяют логику регистрации пользователей.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from src.auth.service import UserService


@pytest.mark.asyncio
async def test_example():
    assert 1 == 1

@pytest.mark.asyncio
async def test_successful_sign_up(async_client):
    """
    Проверяем успешную регистрацию.
    Тест должен пройти весь цикл: роутер -> Dishka -> Сервис -> Хэширование -> БД -> Возврат.
    """
    user_data = {
        "username": "test_user_1",
        "password": "strong_password_123"
    }

    response = await async_client.post("/api/auth/sign-up", json=user_data)

    # Ожидаем 200 OK или 201 Created
    assert response.status_code == 200

    # Проверяем, что в ответе вернулся токен (или ID сессии, в зависимости от твоей схемы)
    data = response.json()
    assert "session_id" in data
    assert isinstance(data["session_id"], str)


async def test_duplicate_username_sign_up(async_client):
    """
    Проверяем логику исключений: нельзя создать двух юзеров с одинаковым именем.
    """
    user_data = {
        "username": "unique_user",
        "password": "password"
    }

    # Первый запрос — успешный
    await async_client.post("/api/auth/sign-up", json=user_data)

    # Второй запрос с теми же данными
    response = await async_client.post("/api/auth/sign-up", json=user_data)

    # Ожидаем 409 Conflict, как у тебя написано в роутере
    assert response.status_code == 409
    assert response.json()["detail"] == "User already exists"