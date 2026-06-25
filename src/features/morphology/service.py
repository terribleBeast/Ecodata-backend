from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.morphology.repository import (
    LeafMorphologicalFeatureValueRepo,
    MeasurementUnitRepo,
    MorphologicalFeatureRepo,
)
from src.shared.database import get_db
from src.shared.service import BaseService
from src.shared.types import PyUUID

# ── Repo factories ─────────────────────────────────────────────────


async def get_measurement_unit_repo(
    session: AsyncSession = Depends(get_db),
) -> MeasurementUnitRepo:
    return MeasurementUnitRepo(session)


async def get_morphological_feature_repo(
    session: AsyncSession = Depends(get_db),
) -> MorphologicalFeatureRepo:
    return MorphologicalFeatureRepo(session)


async def get_leaf_morphological_feature_value_repo(
    session: AsyncSession = Depends(get_db),
) -> LeafMorphologicalFeatureValueRepo:
    return LeafMorphologicalFeatureValueRepo(session)


# ── Services ───────────────────────────────────────────────────────


class MeasurementUnitService(BaseService):
    def __init__(self, repo: MeasurementUnitRepo):
        self._repo = repo


class MorphologicalFeatureService(BaseService):
    def __init__(self, repo: MorphologicalFeatureRepo):
        self._repo = repo


class LeafMorphologicalFeatureValueService:
    """Service for composite-PK entity — does not inherit BaseService."""

    def __init__(self, repo: LeafMorphologicalFeatureValueRepo):
        self._repo = repo

    async def get_one(self, leaf_id: PyUUID, morphological_feature_id: PyUUID):
        return await self._repo.get_by_ids(leaf_id, morphological_feature_id)

    async def create(self, item: BaseModel) -> None:
        item_dict = item.model_dump()
        await self._repo.create(item_dict)

    async def update_value(
        self,
        leaf_id: PyUUID,
        morphological_feature_id: PyUUID,
        item: BaseModel,
    ) -> None:
        await self._repo.update_by_ids(
            leaf_id, morphological_feature_id, item.model_dump(exclude_unset=True)
        )

    async def delete(self, leaf_id: PyUUID, morphological_feature_id: PyUUID) -> None:
        await self._repo.delete_by_ids(leaf_id, morphological_feature_id)


# ── Service factories ──────────────────────────────────────────────


async def get_measurement_unit_service(
    repo: MeasurementUnitRepo = Depends(get_measurement_unit_repo),
) -> MeasurementUnitService:
    return MeasurementUnitService(repo)


async def get_morphological_feature_service(
    repo: MorphologicalFeatureRepo = Depends(get_morphological_feature_repo),
) -> MorphologicalFeatureService:
    return MorphologicalFeatureService(repo)


async def get_leaf_morphological_feature_value_service(
    repo: LeafMorphologicalFeatureValueRepo = Depends(
        get_leaf_morphological_feature_value_repo
    ),
) -> LeafMorphologicalFeatureValueService:
    return LeafMorphologicalFeatureValueService(repo)
