import logging
from typing import AsyncGenerator, Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.settings import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    url=settings.db_url,
    echo=True, # надо ли выводить инфу о выполняемых запросах
    pool_pre_ping=True # перед использовании соединения проверяет живо ли оно и восстанавливает при потере
)
logger.debug("инициализировал движок БД, %s", engine.url.render_as_string(hide_password=True))

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)
logger.debug("создал фабрику сессий и подключил ее к движку БД, %s", async_session)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    logger.debug("запускаю сессию")

    async with async_session() as session:
        logger.debug("запустил сессию %s", session)
        yield session # превращает функцию в генератор, Она "замораживается" и сессия закроется позже


