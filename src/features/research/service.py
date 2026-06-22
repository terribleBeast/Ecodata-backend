from typing import Any

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.research.repository import ResearchRepo
from src.shared.database import get_db
from src.shared.types import PyUUID


async def get_research_repo(
    session: AsyncSession = Depends(get_db),
) -> ResearchRepo:
    return ResearchRepo(session)


class ResearchService:
    """Research project business logic."""

    def __init__(self, repo: ResearchRepo):
        self._repo = repo

    async def get_all(self):
        return await self._repo.get_all()

    async def get_one(self, id: PyUUID):
        return await self._repo.get_by_id(id)

    async def create(self, item: BaseModel) -> PyUUID:
        identity = self._repo.new_id()
        item_dict = item.model_dump()
        item_dict["id"] = identity
        await self._repo.create(item_dict)
        return identity

    async def delete(self, id: PyUUID):
        await self._repo.delete(id)

    async def search_by_field(self, field: str, value: Any):
        return await self._repo.search_by_field(field, value)


async def get_research_service(
    repo: ResearchRepo = Depends(get_research_repo),
) -> ResearchService:
    return ResearchService(repo)
