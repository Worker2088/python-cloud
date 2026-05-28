import json
import logging
from pathlib import Path

from fastapi import FastAPI
from src.auth.router import router as user_router


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


app = FastAPI()
logger.debug("создал app %s", app)

# подключи группу роутов router к приложению app
app.include_router(user_router)
