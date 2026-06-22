from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.jobs.repository import JobRepo
from src.shared.database import get_db
from src.shared.service import BaseService


async def get_job_repo(session: AsyncSession = Depends(get_db)) -> JobRepo:
    return JobRepo(session)


class JobService(BaseService[JobRepo]):
    def __init__(self, repo: JobRepo):
        self._repo = repo


async def get_job_service(
    repo: JobRepo = Depends(get_job_repo),
) -> JobService:
    return JobService(repo)
