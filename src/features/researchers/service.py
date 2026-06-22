from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.researchers.repository import ResearcherRepo
from src.shared.database import get_db
from src.shared.service import BaseService


async def get_researcher_repo(
    session: AsyncSession = Depends(get_db),
) -> ResearcherRepo:
    return ResearcherRepo(session)


class ResearcherService(BaseService[ResearcherRepo]):
    """Researcher profile business logic."""

    def __init__(self, repo: ResearcherRepo):
        self._repo = repo


async def get_researcher_service(
    repo: ResearcherRepo = Depends(get_researcher_repo),
) -> ResearcherService:
    return ResearcherService(repo)
