from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def check_db(session: AsyncSession) -> int:
    result = await session.execute(select(1))
    return result.scalar_one()