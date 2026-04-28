from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.deps import plant_service
from src.database.models.plant import PyUUID
from src.database.repository import PlantRepo
from src.services.base import BaseService
from src.shemas.plant import PlantCreate

router = APIRouter(prefix="/plant", tags=["plant"])


@router.get("/")
async def plant_list(service: Annotated[BaseService, Depends(plant_service)]):
    items = await service.get_all()
    return items


@router.post("/")
async def plant_create(
    service: Annotated[BaseService, Depends(plant_service)], plant: PlantCreate
):
    result = await service.create(plant)
    return result


@router.delete("/")
async def plant_delete(
    service: Annotated[BaseService, Depends(plant_service)], id: PyUUID
):
    await service.delete(id)


@router.get("/search/{genus}")
async def plant_select_by_genus(
    genus: str, service: Annotated[BaseService, Depends(plant_service)]
):
    result = await service.search_by_field("genus", genus)

    return result
