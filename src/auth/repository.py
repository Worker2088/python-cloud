import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exception import UserAlreadyExistsError, DatabaseError
from src.auth.models import User


logger = logging.getLogger(__name__)


class UserRepository():
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create_user(self, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)

        self.session.add(user)

        # тк поле username у нас unique=True, то ловим ошибку в репо
        try:
            await self.session.commit()
        except IntegrityError as e:
            logger.debug("ОШИБКА, юзер с таким именем уже есть в БД, %s", username)

            # отмена транзакции тк была ошибка и чтобы дальше работать с БД ошибочную транзу надо откатить
            await self.session.rollback()
            logger.debug("отменяю транзакцию")

            # ловим нужную нам ошибку UNIQUE violation - ошибка уникальности поля, ее код 23505
            if getattr(e.orig, "sqlstate", None) == "23505":
                raise UserAlreadyExistsError()
            else:
                # ловим все остальные ошибки БД, чтобы прил не упало
                raise DatabaseError()

        await self.session.refresh(user)
        logger.debug("new user, %s", user)
        return user


    async def get_user_by_id(self, user_id: int) -> User | None:
        logger.debug("user_id, %s", user_id)

        result = await self.session.execute(select(User).where(User.id == user_id))
        logger.debug("result, %s", result)
        user = result.scalar_one_or_none()

        return user


    async def get_user_by_name(self, user_name: str) -> User | None:
        logger.debug("user_name, %s", user_name)

        result = await self.session.execute(select(User).where(User.username == user_name))
        logger.debug("result, %s", result)
        user = result.scalar_one_or_none()

        return user


# удаление
# await self.session.delete(user)
# await self.session.commit()
# апдейт
# user = await self.session.get(User, user_id)
# user.username = new_username
# await self.session.commit()
# await self.session.refresh(user)
