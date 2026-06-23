from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.plants.repository import (
    LeafBladeTypeRepo,
    LocationOnPlantRepo,
    PlantDescriptionRepo,
    PlantLifeFormRepo,
    PlantRepo,
    SideOfTheWorldRepo,
)
from src.shared.database import get_db
from src.shared.service import BaseService

# ── Repo factories ────────────────────────────────────────────


async def get_plant_repo(s: AsyncSession = Depends(get_db)) -> PlantRepo:
    return PlantRepo(s)


async def get_plant_life_form_repo(
    s: AsyncSession = Depends(get_db),
) -> PlantLifeFormRepo:
    return PlantLifeFormRepo(s)


async def get_leaf_blade_type_repo(
    s: AsyncSession = Depends(get_db),
) -> LeafBladeTypeRepo:
    return LeafBladeTypeRepo(s)


async def get_plant_description_repo(
    s: AsyncSession = Depends(get_db),
) -> PlantDescriptionRepo:
    return PlantDescriptionRepo(s)


async def get_side_of_the_world_repo(
    s: AsyncSession = Depends(get_db),
) -> SideOfTheWorldRepo:
    return SideOfTheWorldRepo(s)


async def get_location_on_plant_repo(
    s: AsyncSession = Depends(get_db),
) -> LocationOnPlantRepo:
    return LocationOnPlantRepo(s)


# ── Services ──────────────────────────────────────────────────


class PlantService(BaseService[PlantRepo]):
    def __init__(self, repo: PlantRepo):
        self._repo = repo


class PlantLifeFormService(BaseService[PlantLifeFormRepo]):
    def __init__(self, repo: PlantLifeFormRepo):
        self._repo = repo


class LeafBladeTypeService(BaseService[LeafBladeTypeRepo]):
    def __init__(self, repo: LeafBladeTypeRepo):
        self._repo = repo


class PlantDescriptionService(BaseService[PlantDescriptionRepo]):
    def __init__(self, repo: PlantDescriptionRepo):
        self._repo = repo


class SideOfTheWorldService(BaseService[SideOfTheWorldRepo]):
    def __init__(self, repo: SideOfTheWorldRepo):
        self._repo = repo


class LocationOnPlantService(BaseService[LocationOnPlantRepo]):
    def __init__(self, repo: LocationOnPlantRepo):
        self._repo = repo


# ── Service factories ─────────────────────────────────────────


async def get_plant_service(
    repo: PlantRepo = Depends(get_plant_repo),
) -> PlantService:
    return PlantService(repo)


async def get_plant_life_form_service(
    repo: PlantLifeFormRepo = Depends(get_plant_life_form_repo),
) -> PlantLifeFormService:
    return PlantLifeFormService(repo)


async def get_leaf_blade_type_service(
    repo: LeafBladeTypeRepo = Depends(get_leaf_blade_type_repo),
) -> LeafBladeTypeService:
    return LeafBladeTypeService(repo)


async def get_plant_description_service(
    repo: PlantDescriptionRepo = Depends(get_plant_description_repo),
) -> PlantDescriptionService:
    return PlantDescriptionService(repo)


async def get_side_of_the_world_service(
    repo: SideOfTheWorldRepo = Depends(get_side_of_the_world_repo),
) -> SideOfTheWorldService:
    return SideOfTheWorldService(repo)


async def get_location_on_plant_service(
    repo: LocationOnPlantRepo = Depends(get_location_on_plant_repo),
) -> LocationOnPlantService:
    return LocationOnPlantService(repo)
