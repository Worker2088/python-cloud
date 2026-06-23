"""
Главный модуль приложения FastAPI.

Отвечает за:
- инициализацию FastAPI приложения
- подключение роутеров (auth, storage)
- настройку DI контейнера (Dishka)
- настройку CORS
- загрузку конфигурации логирования
- обработку глобальных исключений
"""

import json
import logging.config
from pathlib import Path

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.auth.exception import BaseAppException
from src.auth.providers import AdaptersProvider, InfrastructureProvider
from src.auth.router import router as user_router
from src.storage.providers import StorageProvider
from src.storage.router import router as storage_router
from src.core.middleware.logging import LoggingMiddleware
from src.core.settings import Settings

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
config = None


# --------------------------------------------
# загрузка logging конфигурации из JSON файла

try:
    with open(BASE_DIR / "logs" / "logging.json", "r") as file:
        config = json.load(file)

except (json.JSONDecodeError, FileNotFoundError):
    config = None


if config:
    # применение logging конфигурации
    logging.config.dictConfig(config)


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация всех обработчиков ошибок для приложения."""

    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(request: Request, exc: BaseAppException):
        """
        Обработчик бизнес-исключений приложения.

        Логирует:
        - тип ошибки
        - статус код
        - сообщение
        - путь запроса

        Возвращает:
        - JSON error response
        """

        logger.info(
            "business_exception",
            extra={
                "exception_type": exc.__class__.__name__,
                "status_code": exc.status_code,
                "error_message": exc.message,
                "path": request.url.path,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Обработчик HTTP ошибок Starlette.

        Например:
        - 404 Not Found
        """

        if exc.status_code == 404:
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": "Ресурс не найден"},
            )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ):
        """
        Ловит все необработанные исключения.

        Используется как safety net (fallback handler).

        Логирует:
        - stack trace (exc_info=True)
        - путь запроса
        - HTTP метод

        Возвращает:
        - 500 Internal Server Error
        """

        logger.error(
            "unexpected_exception",
            exc_info=True,
            extra={
                "path": request.url.path,
                "method": request.method,
            },
        )

        return JSONResponse(
            status_code=500, content={"message": "Internal server error"}
        )


def create_app(container_dishka=None) -> FastAPI:
    """
    Фабрика FastAPI приложения.

    Отвечает за:
    - регистрацию роутеров
    - настройку DI контейнера
    - подключение middleware (CORS, logging)
    """

    app = FastAPI()
    logger.info("создал app %s", app)

    app.include_router(user_router)
    app.include_router(storage_router)

    app.add_middleware(LoggingMiddleware)

    # --------------------------------------------
    # CORS настройка (frontend → backend доступ)

    origins = [
        "http://localhost:5173",
        "http://localhost:80",
        "http://localhost",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --------------------------------------------
    # DI контейнер (Dishka)

    if container_dishka is None:
        app_settings = Settings()

        container_dishka = make_async_container(
            AdaptersProvider(),
            StorageProvider(),
            InfrastructureProvider(),
            context={Settings: app_settings},
        )

    setup_dishka(container_dishka, app)

    # регистрируем обработчики, чтобы при вызове create_app
    # они автоматом регистрировались и работали напр в тестовом окружении
    register_exception_handlers(app)

    return app


app = create_app()


@app.get("/api/v1/healthcheck")
def healthcheck():
    """
    Проверка работоспособности сервиса.

    Returns:
        dict: статус сервиса
    """
    return {"status": "ok"}
