from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.features.leaves.models import Leaf, LeafArtifact
from src.shared.repository import SqlRepo


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
