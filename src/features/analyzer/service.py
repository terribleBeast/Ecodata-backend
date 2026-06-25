from typing import Any

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.analyzer.repository import NeuralModelRepo
from src.shared.database import get_db
from src.shared.service import BaseService
from src.shared.types import PyUUID


async def get_neural_model_repo(
    session: AsyncSession = Depends(get_db),
) -> NeuralModelRepo:
    return NeuralModelRepo(session)


class NeuralModelService(BaseService[NeuralModelRepo]):
    def __init__(self, repo: NeuralModelRepo):
        self._repo = repo

    async def get_by_species(self, species_id: list[PyUUID]):
        return await self._repo.get_by_species(species_id)


async def get_neural_model_service(
    repo: NeuralModelRepo = Depends(get_neural_model_repo),
) -> NeuralModelService:
    return NeuralModelService(repo)
