from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.features.morphology.models import (
    LeafMorphologicalFeatureValue,
    MeasurementUnit,
    MorphologicalFeature,
)
from src.shared.repository import SqlRepo
from src.shared.types import PyUUID


class MeasurementUnitRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(MeasurementUnit, session)


class MorphologicalFeatureRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(MorphologicalFeature, session)

    async def get_by_id(self, id: UUID):
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(MorphologicalFeature.default_unit))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(MorphologicalFeature.default_unit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class LeafMorphologicalFeatureValueRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(LeafMorphologicalFeatureValue, session)

    async def get_by_ids(self, leaf_id: PyUUID, mf_id: PyUUID):
        stmt = (
            select(self.model)
            .where(self.model.leaf_id == leaf_id)
            .where(self.model.morphological_feature_id == mf_id)
            .options(
                selectinload(LeafMorphologicalFeatureValue.leaf),
                selectinload(LeafMorphologicalFeatureValue.morphological_feature),
                selectinload(LeafMorphologicalFeatureValue.measurement_unit),
                selectinload(LeafMorphologicalFeatureValue.measured_by_model),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_ids(self, leaf_id: PyUUID, mf_id: PyUUID) -> None:
        stmt = (
            delete(self.model)
            .where(self.model.leaf_id == leaf_id)
            .where(self.model.morphological_feature_id == mf_id)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_by_ids(
        self, leaf_id: PyUUID, mf_id: PyUUID, changes: dict[str, Any]
    ) -> None:
        stmt = (
            update(self.model)
            .where(self.model.leaf_id == leaf_id)
            .where(self.model.morphological_feature_id == mf_id)
            .values(**changes)
        )
        await self.session.execute(stmt)
        await self.session.commit()
