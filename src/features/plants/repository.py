from sqlalchemy.ext.asyncio import AsyncSession
from src.features.plants.models import (
    LeafBladeType,
    LocationOnPlant,
    Plant,
    PlantDescription,
    PlantLifeForm,
    SideOfTheWorld,
)
from src.shared.repository import SqlRepo


class PlantRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Plant, session)


class PlantLifeFormRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(PlantLifeForm, session)


class LeafBladeTypeRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(LeafBladeType, session)


class PlantDescriptionRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(PlantDescription, session)


class SideOfTheWorldRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(SideOfTheWorld, session)


class LocationOnPlantRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(LocationOnPlant, session)
