from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.features.plants.models import Plant, PlantDescription
from src.features.research.models import (
    Research,
    ResearcherResearchAssociation,
    ResearchPlantAssociation,
)
from src.shared.repository import SqlRepo
from src.shared.types import PyUUID


def _research_load_options():
    return (
        selectinload(Research.created_by),
        selectinload(Research.participants),
        selectinload(Research.plants).selectinload(Plant.location),
        selectinload(Research.plants)
        .selectinload(Plant.plant_description)
        .selectinload(PlantDescription.species),
        selectinload(Research.plants)
        .selectinload(Plant.plant_description)
        .selectinload(PlantDescription.plant_life_form),
        selectinload(Research.plants)
        .selectinload(Plant.plant_description)
        .selectinload(PlantDescription.leaf_blade_type),
    )


class ResearchRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Research, session)

    async def get_by_id(self, id):
        stmt = (
            select(self.model)
            .options(
                selectinload(Research.created_by),
                selectinload(Research.participants),
            )
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(Research.created_by),
            selectinload(Research.participants),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_by_status(self, status: str) -> list[Research]:
        stmt = (
            select(Research)
            .options(
                selectinload(Research.created_by),
                selectinload(Research.participants),
            )
            .where(Research.status == status)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_researchers(
        self, research_id: PyUUID, researcher_ids: list[PyUUID]
    ) -> None:
        values = [
            {"research_id": research_id, "researcher_id": rid} for rid in researcher_ids
        ]
        stmt = insert(ResearcherResearchAssociation).values(values)
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_researchers(
        self, research_id: PyUUID, researcher_ids: list[PyUUID]
    ) -> None:
        stmt = delete(ResearcherResearchAssociation).where(
            ResearcherResearchAssociation.research_id == research_id,
            ResearcherResearchAssociation.researcher_id.in_(researcher_ids),
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def set_researchers(
        self, research_id: PyUUID, researcher_ids: list[PyUUID]
    ) -> None:
        # replace the whole set atomically
        async with self.session.begin():
            await self.session.execute(
                delete(ResearcherResearchAssociation).where(
                    ResearcherResearchAssociation.research_id == research_id
                )
            )
            if researcher_ids:
                values = [
                    {"research_id": research_id, "researcher_id": rid}
                    for rid in researcher_ids
                ]
                await self.session.execute(
                    insert(ResearcherResearchAssociation).values(values)
                )

    async def add_plants(self, research_id: PyUUID, plant_ids: list[PyUUID]) -> None:
        plant_ids = list(dict.fromkeys(plant_ids))
        if not plant_ids:
            return

        values = [{"research_id": research_id, "plant_id": pid} for pid in plant_ids]
        stmt = insert(ResearchPlantAssociation).values(values)

        await self.session.execute(stmt)
        await self.session.commit()

    async def set_plants(self, research_id: PyUUID, plant_ids: list[PyUUID]) -> None:
        plant_ids = list(dict.fromkeys(plant_ids))

        async with self.session.begin():
            await self.session.execute(
                delete(ResearchPlantAssociation).where(
                    ResearchPlantAssociation.research_id == research_id
                )
            )

            if plant_ids:
                values = [
                    {"research_id": research_id, "plant_id": pid} for pid in plant_ids
                ]
                await self.session.execute(
                    insert(ResearchPlantAssociation).values(values)
                )
