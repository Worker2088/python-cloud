import logging

from fastapi import HTTPException

from src.auth.exception import UserNotFoundError
from src.auth.interfaces import IUserRepository
from src.auth.schemas import UserRegistrationDTOResponse, UserRegistrationDTO

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    async def create_user(self, user_dto: UserRegistrationDTO) -> UserRegistrationDTOResponse:
        logger.debug("!!!создаю юзера %s", user_dto)

        hashed_password = user_dto.password

        user_model = await self.repo.create_user(
            username=user_dto.username,
            hashed_password=hashed_password)

        logger.debug("!!!user_model, %s", user_model)

        return UserRegistrationDTOResponse.model_validate(user_model)

    async def get_user(self, user_id: int) -> UserRegistrationDTOResponse:
        user = await self.repo.get_user_id(user_id=user_id)

        if user is None:
            logger.debug("!!!юзера НЕ нашли, %s", user)
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        logger.debug("!!!юзера нашли, %s", user)
        return UserRegistrationDTOResponse.model_validate(user)
