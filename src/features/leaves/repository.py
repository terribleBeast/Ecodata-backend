from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy.sql import update
from src.features.leaves.models import Leaf, LeafArtifact
from src.features.plants.models import Plant, PlantDescription
from src.features.taxonomy.models import Species
from src.shared.repository import SqlRepo
from src.shared.types import PyUUID


class LeafRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Leaf, session)

    async def get_by_id(self, id):
        stmt = (
            select(self.model)
            .options(
                selectinload(Leaf.plant),
                selectinload(Leaf.image),
                selectinload(Leaf.side_of_the_world),
                selectinload(Leaf.location_on_plant),
            )
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(Leaf.plant),
            selectinload(Leaf.image),
            selectinload(Leaf.side_of_the_world),
            selectinload(Leaf.location_on_plant),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_leaf_genus_id(self, leaf_id: PyUUID) -> PyUUID | None:
        current_plant = aliased(Plant)
        description = aliased(PlantDescription)
        species = aliased(Species)

        stmt = (
            select(species.genus_id)
            .select_from(Leaf)
            .join(current_plant, Leaf.plant_id == current_plant.id)
            .join(description, current_plant.plant_description_id == description.id)
            .join(species, description.species_id == species.id)
            .where(Leaf.id == leaf_id)
        )

        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_plant_genus_id(self, plant_id: PyUUID) -> PyUUID | None:
        stmt = (
            select(Species.genus_id)
            .select_from(Plant)
            .join(PlantDescription, Plant.plant_description_id == PlantDescription.id)
            .join(Species, PlantDescription.species_id == Species.id)
            .where(Plant.id == plant_id)
        )

        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def assign_plants_to_leaves(
        self,
        assignments: list[dict[str, PyUUID]],
    ) -> None:
        async with self.session.begin():
            for assignment in assignments:
                leaf_id = assignment["leaf_id"]
                plant_id = assignment["plant_id"]

                leaf_genus_id = await self.get_leaf_genus_id(leaf_id)
                plant_genus_id = await self.get_plant_genus_id(plant_id)

                if leaf_genus_id is None:
                    raise ValueError(f"Leaf {leaf_id} has no genus context")

                if plant_genus_id is None:
                    raise ValueError(f"Plant {plant_id} has no genus context")

                if leaf_genus_id != plant_genus_id:
                    raise ValueError(
                        f"Leaf {leaf_id} and plant {plant_id} have different genera"
                    )

            for assignment in assignments:
                await self.session.execute(
                    update(Leaf)
                    .where(Leaf.id == assignment["leaf_id"])
                    .values(plant_id=assignment["plant_id"])
                )


class LeafArtifactRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(LeafArtifact, session)

    async def get_by_id(self, id):
        stmt = (
            select(self.model)
            .options(
                selectinload(LeafArtifact.leaf),
                selectinload(LeafArtifact.file),
                selectinload(LeafArtifact.created_by_model),
            )
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(LeafArtifact.leaf),
            selectinload(LeafArtifact.file),
            selectinload(LeafArtifact.created_by_model),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
