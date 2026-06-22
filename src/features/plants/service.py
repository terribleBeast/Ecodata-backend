from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.plants.repository import PlantRepo
from src.shared.database import get_db
from src.shared.service import BaseService


async def get_plant_repo(session: AsyncSession = Depends(get_db)) -> PlantRepo:
    return PlantRepo(session)


class PlantService(BaseService):
    """Plant taxonomy business logic."""

    def __init__(self, repo: PlantRepo):
        self._repo = repo

    # async def get_all(self):
    #     return await self._repo.get_all()

    # async def get_one(self, id: PyUUID):
    #     return await self._repo.get_by_id(id)

    # async def create(self, item: BaseModel) -> PyUUID:
    #     identity = self._repo.new_id()
    #     item_dict = item.model_dump()
    #     item_dict["id"] = identity
    #     await self._repo.create(item_dict)
    #     return identity

    # async def delete(self, id: PyUUID):
    #     await self._repo.delete(id)

    # async def search_by_field(self, field: str, value: Any):
    #     return await self._repo.search_by_field(field, value)


async def get_plant_service(
    repo: PlantRepo = Depends(get_plant_repo),
) -> PlantService:
    return PlantService(repo)
