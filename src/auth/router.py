import logging

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path

from src.auth.schemas import UserRegistrationDTO, UserRegistrationDTOResponse
from src.auth.service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth") # создай mini-app для группы роутов
# router это папка/контейнер с группой endpoint'ов


@router.post("/sign-up", response_model=UserRegistrationDTOResponse)
@inject  # <-- ОБЯЗАТЕЛЬНО: этот декоратор заставляет Dishka искать маркеры в аргументах
async def create_user(
        create_user_dto: UserRegistrationDTO,
        user_service: FromDishka[UserService]
        # Говорим Дишке: "достань мне этот класс из контейнера"
        ):
    logger.debug("!!!create_user_dto, %s", create_user_dto)

    user = await user_service.create_user(create_user_dto)
    return user

@router.get("/", response_model=UserRegistrationDTOResponse)
@inject  # <-- ОБЯЗАТЕЛЬНО: этот декоратор заставляет Dishka искать маркеры в аргументах
async def get_user(
        user_id: int,
        user_service: FromDishka[UserService]
        # Говорим Дишке: "достань мне этот класс из контейнера"
        ):
    logger.debug("!!!user_id, %s", user_id)

    user = await user_service.get_user(user_id)
    return user





