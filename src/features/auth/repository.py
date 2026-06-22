from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.auth.models import SystemRole, User
from src.shared.repository import SqlRepo


class SystemRoleRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(SystemRole, session)


class UserRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
