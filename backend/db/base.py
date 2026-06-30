"""
Базовый класс ORM моделей SQLAlchemy.

Назначение:
- является общей базой для всех моделей в приложении
- используется SQLAlchemy Declarative Base system
- позволяет SQLAlchemy автоматически регистрировать модели
  и строить таблицы на основе классов
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Базовый класс для всех ORM моделей.

    Используется как родительский класс для всех моделей,
    чтобы SQLAlchemy мог:
    - регистрировать модели
    - строить metadata
    - выполнять миграции (через Alembic)
    """

    ...
