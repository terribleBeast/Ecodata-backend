from sqlalchemy.ext.asyncio import AsyncSession
from src.features.jobs.models import Job
from src.shared.repository import SqlRepo


class JobRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Job, session)
