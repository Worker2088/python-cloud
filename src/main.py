import json
import logging
from pathlib import Path

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.auth.dependencies import AdaptersProvider, InfrastructureProvider, IntegrationsProvider, UtilsProvider
from src.auth.router import router as user_router
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


def create_app() -> FastAPI:
    app = FastAPI()
    logger.debug("создал app %s", app)
    # подключил группу роутов router к приложению app
    app.include_router(user_router)

    # Читаем настройки НА СТАРТЕ приложения.
    # Если в .env ошибка — код упадет прямо здесь, жестко и сразу.
    app_settings = Settings()

    # 1. Создаем контейнер и передаем наши провайдеры
    container_dishka = make_async_container(
        AdaptersProvider(),
        InfrastructureProvider(),
        IntegrationsProvider(),
        UtilsProvider(),
        context={Settings: app_settings} # в контекст дишки отправляем настройки
    )

    # 2. Интегрируем Dishka в FastAPI
    setup_dishka(container_dishka, app)

    return app


app = create_app()