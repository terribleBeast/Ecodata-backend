from sqlalchemy.ext.asyncio import AsyncSession
from src.features.auth.models import SystemRole
from src.shared.repository import SqlRepo


class SystemRoleRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(SystemRole, session)
