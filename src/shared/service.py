from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from src.shared.repository import SqlRepo
from src.shared.types import PyUUID

Repo = TypeVar("Repo", bound=SqlRepo)


class BaseService(Generic[Repo]):
    # class BaseService:
    def __init__(self, repo: Repo):
        self._repo = repo

    async def get_all(self):
        return await self._repo.get_all()

    async def get_one(self, id):
        return await self._repo.get_by_id(id)

    async def create(self, item: BaseModel):
        identity = self._repo.new_id()
        item_dict = item.model_dump()
        item_dict["id"] = identity
        await self._repo.create(item_dict)
        return identity

    async def update(self, id: PyUUID, item: BaseModel):
        await self._repo.update(id, item.model_dump())
        return id

    async def delete(self, id: PyUUID):
        await self._repo.delete(id)

    async def search_by_field(self, field: str, value: Any):
        return await self._repo.search_by_field(field, value)
