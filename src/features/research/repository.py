from sqlalchemy.ext.asyncio import AsyncSession
from src.features.research.models import Research
from src.shared.repository import SqlRepo


class ResearchRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Research, session)
