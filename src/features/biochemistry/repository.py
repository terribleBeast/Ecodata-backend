from typing import Any
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.features.biochemistry.models import (
    BiochemicalAnalysis,
    BiochemicalAnalysisValue,
    BiochemicalIndicator,
    Laboratory,
)
from src.shared.repository import SqlRepo

# ── Laboratory ─────────────────────────────────────────────────


class LaboratoryRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Laboratory, session)

    async def get_by_id(self, id: UUID):
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(Laboratory.organization),
                selectinload(Laboratory.address),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(Laboratory.organization),
            selectinload(Laboratory.address),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ── BiochemicalIndicator ───────────────────────────────────────


class BiochemicalIndicatorRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(BiochemicalIndicator, session)

    async def get_by_id(self, id: UUID):
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(BiochemicalIndicator.default_unit))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(BiochemicalIndicator.default_unit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ── BiochemicalAnalysis ────────────────────────────────────────


class BiochemicalAnalysisRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(BiochemicalAnalysis, session)

    async def get_by_id(self, id: UUID):
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(BiochemicalAnalysis.plant),
                selectinload(BiochemicalAnalysis.laboratory),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(BiochemicalAnalysis.plant),
            selectinload(BiochemicalAnalysis.laboratory),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ── BiochemicalAnalysisValue ───────────────────────────────────


class BiochemicalAnalysisValueRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(BiochemicalAnalysisValue, session)

    async def get_by_analysis_id(self, analysis_id: UUID):
        stmt = (
            select(self.model)
            .where(self.model.biochemical_analysis_id == analysis_id)
            .options(
                selectinload(BiochemicalAnalysisValue.indicator),
                selectinload(BiochemicalAnalysisValue.measurement_unit),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_composite_key(self, analysis_id: UUID, indicator_id: UUID):
        stmt = (
            select(self.model)
            .where(
                self.model.biochemical_analysis_id == analysis_id,
                self.model.biochemical_indicator_id == indicator_id,
            )
            .options(
                selectinload(BiochemicalAnalysisValue.indicator),
                selectinload(BiochemicalAnalysisValue.measurement_unit),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_value(self, item: dict[str, Any]) -> None:
        stmt = insert(self.model).values(**item)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_by_composite_key(
        self, analysis_id: UUID, indicator_id: UUID
    ) -> None:
        stmt = (
            delete(self.model)
            .where(self.model.biochemical_analysis_id == analysis_id)
            .where(self.model.biochemical_indicator_id == indicator_id)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_value(
        self, analysis_id: UUID, indicator_id: UUID, changes: dict[str, Any]
    ) -> None:
        stmt = (
            update(self.model)
            .where(self.model.biochemical_analysis_id == analysis_id)
            .where(self.model.biochemical_indicator_id == indicator_id)
            .values(**changes)
        )
        await self.session.execute(stmt)
        await self.session.commit()
