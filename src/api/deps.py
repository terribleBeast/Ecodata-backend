from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dependencies import get_db
from src.database.repository import NeuralModelRepo, PlantRepo
from src.services.base import BaseService


async def get_plant_repo(session: AsyncSession = Depends(get_db)) -> PlantRepo:
    return PlantRepo(session)


async def plant_service(repo: PlantRepo = Depends(get_plant_repo)):
    return BaseService(repo)


async def get_neural_model_repo(
    session: AsyncSession = Depends(get_db),
) -> NeuralModelRepo:
    return NeuralModelRepo(session)


async def neural_model_service(repo: NeuralModelRepo = Depends(get_neural_model_repo)):
    return BaseService(repo)
