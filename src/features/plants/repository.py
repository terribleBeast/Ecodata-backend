from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
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

    async def get_by_id(self, id):
        stmt = (
            select(Plant)
            .where(Plant.id == id)
            .options(
                selectinload(Plant.location),
                selectinload(Plant.plant_description).selectinload(
                    PlantDescription.species
                ),
                selectinload(Plant.plant_description).selectinload(
                    PlantDescription.plant_life_form
                ),
                selectinload(Plant.plant_description).selectinload(
                    PlantDescription.leaf_blade_type
                ),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(Plant).options(
            selectinload(Plant.location),
            selectinload(Plant.plant_description).selectinload(
                PlantDescription.species
            ),
            selectinload(Plant.plant_description).selectinload(
                PlantDescription.plant_life_form
            ),
            selectinload(Plant.plant_description).selectinload(
                PlantDescription.leaf_blade_type
            ),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class PlantLifeFormRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(PlantLifeForm, session)


class LeafBladeTypeRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(LeafBladeType, session)


class PlantDescriptionRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(PlantDescription, session)

    async def get_by_id(self, id):
        stmt = (
            select(PlantDescription)
            .where(PlantDescription.id == id)
            .options(
                selectinload(PlantDescription.species),
                selectinload(PlantDescription.plant_life_form),
                selectinload(PlantDescription.leaf_blade_type),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(PlantDescription).options(
            selectinload(PlantDescription.species),
            selectinload(PlantDescription.plant_life_form),
            selectinload(PlantDescription.leaf_blade_type),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class SideOfTheWorldRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(SideOfTheWorld, session)


class LocationOnPlantRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(LocationOnPlant, session)
