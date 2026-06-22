from sqlalchemy.ext.asyncio import AsyncSession
from src.features.researchers.models import Researcher
from src.shared.repository import SqlRepo


class ResearcherRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Researcher, session)
