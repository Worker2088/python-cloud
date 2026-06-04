import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from src.core.settings import Settings
from src.db.base import Base
from src.auth.models import User

# Это объект конфигурации Alembic, который предоставляет
# доступ к значениям внутри используемого .ini файла.
config = context.config

db_url = Settings().db_url

if db_url:
    # Экранируем знаки процента %, заменяя их на %%,
    # чтобы configparser не пытался сделать интерполяцию
    escaped_db_url = db_url.replace("%", "%%")

    # Передаем в Alembic уже безопасную строку
    config.set_main_option("sqlalchemy.url", escaped_db_url)

# Настройка логирования Python на основе .ini файла
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Передаем метаданные моделей для поддержки автогенерации (--autogenerate)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме (например, при генерации SQL скриптов)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Вспомогательная функция для выполнения миграций внутри синхронного контекста."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме (с реальным асинхронным подключением к БД)."""

    # Используем асинхронный async_engine_from_config вместо старого синхронного
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def run_async():
        async with connectable.connect() as connection:
            # run_sync помогает выполнить синхронный код Alembic внутри асинхронного соединения
            await connection.run_sync(do_run_migrations)

    # Запускаем асинхронный цикл событий для выполнения подключения
    asyncio.run(run_async())


# Главная точка входа, определяющая режим работы Alembic
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()