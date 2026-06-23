from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.biochemistry.repository import (
    BiochemicalAnalysisRepo,
    BiochemicalAnalysisValueRepo,
    BiochemicalIndicatorRepo,
    LaboratoryRepo,
)
from src.features.biochemistry.schemas import (
    BiochemicalAnalysisValueCreate,
    BiochemicalAnalysisValueUpdate,
)
from src.shared.database import get_db
from src.shared.service import BaseService
from src.shared.types import PyUUID

# ── Laboratory ─────────────────────────────────────────────────


async def get_laboratory_repo(
    session: AsyncSession = Depends(get_db),
) -> LaboratoryRepo:
    return LaboratoryRepo(session)


class LaboratoryService(BaseService[LaboratoryRepo]):
    def __init__(self, repo: LaboratoryRepo):
        self._repo = repo


async def get_laboratory_service(
    repo: LaboratoryRepo = Depends(get_laboratory_repo),
) -> LaboratoryService:
    return LaboratoryService(repo)


# ── BiochemicalIndicator ───────────────────────────────────────


async def get_biochemical_indicator_repo(
    session: AsyncSession = Depends(get_db),
) -> BiochemicalIndicatorRepo:
    return BiochemicalIndicatorRepo(session)


class BiochemicalIndicatorService(BaseService[BiochemicalIndicatorRepo]):
    def __init__(self, repo: BiochemicalIndicatorRepo):
        self._repo = repo


async def get_biochemical_indicator_service(
    repo: BiochemicalIndicatorRepo = Depends(get_biochemical_indicator_repo),
) -> BiochemicalIndicatorService:
    return BiochemicalIndicatorService(repo)


# ── BiochemicalAnalysis ────────────────────────────────────────


async def get_biochemical_analysis_repo(
    session: AsyncSession = Depends(get_db),
) -> BiochemicalAnalysisRepo:
    return BiochemicalAnalysisRepo(session)


class BiochemicalAnalysisService(BaseService[BiochemicalAnalysisRepo]):
    def __init__(self, repo: BiochemicalAnalysisRepo):
        self._repo = repo


async def get_biochemical_analysis_service(
    repo: BiochemicalAnalysisRepo = Depends(get_biochemical_analysis_repo),
) -> BiochemicalAnalysisService:
    return BiochemicalAnalysisService(repo)


# ── BiochemicalAnalysisValue ───────────────────────────────────


async def get_biochemical_analysis_value_repo(
    session: AsyncSession = Depends(get_db),
) -> BiochemicalAnalysisValueRepo:
    return BiochemicalAnalysisValueRepo(session)


class BiochemicalAnalysisValueService:
    def __init__(self, repo: BiochemicalAnalysisValueRepo):
        self._repo = repo

    async def get_by_analysis_id(self, analysis_id: PyUUID):
        return await self._repo.get_by_analysis_id(analysis_id)

    async def get_by_composite_key(self, analysis_id: PyUUID, indicator_id: PyUUID):
        return await self._repo.get_by_composite_key(analysis_id, indicator_id)

    async def create(self, analysis_id: PyUUID, item: BiochemicalAnalysisValueCreate):
        item_dict = item.model_dump()
        item_dict["biochemical_analysis_id"] = analysis_id
        await self._repo.create_value(item_dict)

    async def delete(self, analysis_id: PyUUID, indicator_id: PyUUID):
        await self._repo.delete_by_composite_key(analysis_id, indicator_id)

    async def update(
        self,
        analysis_id: PyUUID,
        indicator_id: PyUUID,
        item: BiochemicalAnalysisValueUpdate,
    ):
        await self._repo.update_value(
            analysis_id, indicator_id, item.model_dump(exclude_unset=True)
        )


async def get_biochemical_analysis_value_service(
    repo: BiochemicalAnalysisValueRepo = Depends(get_biochemical_analysis_value_repo),
) -> BiochemicalAnalysisValueService:
    return BiochemicalAnalysisValueService(repo)
