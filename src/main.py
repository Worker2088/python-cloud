import json
import logging
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


try:
    with open(BASE_DIR / "logs" / "logging.json", "r") as file:
        config = json.load(file)
        print("logging.json успешно прочитан")


except (json.JSONDecodeError, FileNotFoundError):
    config = None
    print("Ошибка загрузки logging.json")

if config:
    # LOGGING = config
    logging.config.dictConfig(config)
    print("LOGGING: JSON CONFIG USED")


def create_app(container_dishka=None) -> FastAPI:
    app = FastAPI()
    logger.debug("создал app %s", app)
    # подключил группу роутов router к приложению app
    app.include_router(user_router)
    app.include_router(storage_router)
    # app.add_middleware(LoggingMiddleware) # сделал чтоб просто посмотреть работу с middleware

    # Указываем адреса, с которых разрешены запросы к API
    origins = [
        "http://localhost:5173",  # Для локальной разработки React (Vite)
        "http://localhost:80",  # Для продакшена через Nginx
        "http://localhost",  # На случай запросов без указания порта
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,  # Важно для работы с куками и сессиями
        allow_methods=["*"],  # Разрешаем все методы (GET, POST, PUT, DELETE)
        allow_headers=["*"],  # Разрешаем все заголовки
    )

    if container_dishka is None:
        # Читаем настройки НА СТАРТЕ приложения.
        # Если в .env ошибка — код упадет прямо здесь, жестко и сразу.
        app_settings = Settings()

        # 1. Создаем контейнер и передаем наши провайдеры
        container_dishka = make_async_container(
            AdaptersProvider(),
            StorageProvider(),
            InfrastructureProvider(),
            context={Settings: app_settings} # в контекст дишки отправляем настройки
        )

    # 2. Интегрируем Dishka в FastAPI
    setup_dishka(container_dishka, app)

    return app


app = create_app()


@app.get("/api/v1/healthcheck")
def healthcheck():
    return {"status": "ok"}


@app.exception_handler(BaseAppException)
async def base_app_exception_handler(request: Request, exc: BaseAppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message},
    )

# ловим HTTP-исключения (Starlette) и формируем ответ по ТЗ
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        # Приводим к формату ТЗ
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": "Ресурс не найден"},  # Или можно взять exc.detail, если хочешь
        )

    # # Для остальных HTTPException (400, 401, 500 и т. п.) тоже можно унифицировать
    # return JSONResponse(
    #     status_code=exc.status_code,
    #     content={"message": exc.detail},
    # )
