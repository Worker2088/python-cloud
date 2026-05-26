import logging

from fastapi import APIRouter, Path

from src.auth.repository import check_db
from src.db.database import DBSessionDepends

logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/user")
router = APIRouter()


# используем параметр path в ручке
@router.get("/{user_id}")
def get_user(user_id: int = Path(ge=1)):  # указываем требования к user_id
    # обычно (чаще всего) Path может int или str или uuid
    return {"user": user_id}


@router.get("/")
async def root(db_session: DBSessionDepends):
    data = await check_db(db_session)

    logger.debug("простой запрос к БД, результат, %s", data)
    logger.debug("db_session, %s", db_session)
    return {"key": data}


# query параметры, параметры после ? в url
# /file?param1=10&param2=20

# def get_file(query: MyClassDTO = Depends()):
# # MyClassDTO это наш Пайдентик класс ДТО для валидации вход.данных,
# # "= Depends()"  говорим что данные берем из входных параметров запроса
#     if query.param1 < 100 or query.param2 < 100:
#         raise MyHTTPException()
#
#     return {"param1": query.param1, "param2": query.param2}#, "tags": query.tags}



# @router.get("/7", response_class=HTMLResponse) # FileResponse
# def root2(response: Response):
#     response.status_code = 201
#     return """
#             <!DOCTYPE html>
#             <html lang="ru">
#             <head>
#                 <meta charset="UTF-8">
#                 <title>Кнопка с приветствием</title>
#             </head>
#             <body>
#                 <button>привет</button>
#             </body>
#             </html>
#             """
# return Response(status_code=200)

