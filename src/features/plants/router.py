from typing import Annotated

from fastapi import APIRouter, Depends
from src.features.plants.schemas import PlantCreate
from src.features.plants.service import PlantService, get_plant_service
from src.shared.types import PyUUID

router = APIRouter(prefix="/plants", tags=["plants"])


@router.get("/")
async def plant_list(
    service: Annotated[PlantService, Depends(get_plant_service)],
    genus: str | None = None,
    species: str | None = None,
):
    items = await service.get_all()
    return items


@router.post("/")
async def plant_create(
    service: Annotated[PlantService, Depends(get_plant_service)],
    plant: PlantCreate,
):
    result = await service.create(plant)
    return result


@router.delete("/{id}")
async def plant_delete(
    id: PyUUID,
    service: Annotated[PlantService, Depends(get_plant_service)],
):
    await service.delete(id)
