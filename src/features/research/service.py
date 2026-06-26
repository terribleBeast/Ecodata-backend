from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.research.repository import ResearchRepo
from src.shared.database import get_db
from src.shared.service import BaseService
from src.shared.types import PyUUID


async def get_research_repo(
    session: AsyncSession = Depends(get_db),
) -> ResearchRepo:
    return ResearchRepo(session)


class ResearchService(BaseService[ResearchRepo]):
    """Research project business logic."""

    def __init__(self, repo: ResearchRepo):
        self._repo = repo

    async def search_by_status(self, status: str):
        return await self._repo.search_by_status(status)

    async def add_researchers(
        self, research_id: PyUUID, researcher_ids: list[PyUUID]
    ) -> None:
        await self._repo.add_researchers(research_id, researcher_ids)

    async def remove_researchers(
        self, research_id: PyUUID, researcher_ids: list[PyUUID]
    ) -> None:
        await self._repo.remove_researchers(research_id, researcher_ids)

    async def set_researchers(
        self, research_id: PyUUID, researcher_ids: list[PyUUID]
    ) -> None:
        await self._repo.set_researchers(research_id, researcher_ids)

    async def create(self, item: BaseModel) -> PyUUID:
        identity = self._repo.new_id()

        item_dict = item.model_dump(exclude={"researcher_ids", "plant_ids"})
        item_dict["id"] = identity

        await self._repo.create(item_dict)

        researcher_ids: list[PyUUID] = getattr(item, "researcher_ids", [])
        if researcher_ids:
            await self._repo.add_researchers(identity, researcher_ids)

        plant_ids: list[PyUUID] = getattr(item, "plant_ids", [])
        if plant_ids:
            await self._repo.add_plants(identity, plant_ids)

        return identity

    async def update(self, id: PyUUID, item: BaseModel) -> PyUUID:
        item_dict = item.model_dump(
            exclude_unset=True,
            exclude={"researcher_ids", "plant_ids"},
        )

        if item_dict:
            await self._repo.update(id, item_dict)

        researcher_ids: list[PyUUID] | None = getattr(item, "researcher_ids", None)
        if researcher_ids is not None:
            await self._repo.set_researchers(id, researcher_ids)

        plant_ids: list[PyUUID] | None = getattr(item, "plant_ids", None)
        if plant_ids is not None:
            await self._repo.set_plants(id, plant_ids)

        return id


async def get_research_service(
    repo: ResearchRepo = Depends(get_research_repo),
) -> ResearchService:
    return ResearchService(repo)
