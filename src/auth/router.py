import logging

from fastapi import APIRouter, Path

from src.auth.dependencies import UserServiceDepends
from src.auth.schemas import UserRegistrationDTO, UserRegistrationDTOResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth") # создай mini-app для группы роутов
# router это папка/контейнер с группой endpoint'ов


@router.post("/sign-up", response_model=UserRegistrationDTOResponse)
async def create_user(create_user_dto: UserRegistrationDTO, user_service: UserServiceDepends):
    logger.debug("!!!create_user_dto, %s", create_user_dto)

    user = await user_service.create_user(create_user_dto)
    return user







