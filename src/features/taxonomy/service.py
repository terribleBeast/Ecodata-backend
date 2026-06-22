from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.taxonomy.repository import GenusRepo, SpeciesRepo
from src.shared.database import get_db
from src.shared.service import BaseService


async def get_genus_repo(session: AsyncSession = Depends(get_db)) -> GenusRepo:
    return GenusRepo(session)


async def get_species_repo(session: AsyncSession = Depends(get_db)) -> SpeciesRepo:
    return SpeciesRepo(session)


class GenusService(BaseService):
    def __init__(self, repo: GenusRepo):
        self._repo = repo


class SpeciesService(BaseService):
    def __init__(self, repo: SpeciesRepo):
        self._repo = repo

    def get_by_genus(self, genus_id: str):
        return self._repo.get_by_genus(genus_id)


async def get_genus_service(
    repo: GenusRepo = Depends(get_genus_repo),
) -> GenusService:
    return GenusService(repo)


async def get_species_service(
    repo: SpeciesRepo = Depends(get_species_repo),
) -> SpeciesService:
    return SpeciesService(repo)
