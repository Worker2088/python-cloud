import logging

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

