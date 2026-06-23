from typing import Annotated

from fastapi import APIRouter, Depends
from src.features.biochemistry.schemas import (
    BiochemicalAnalysisCreate,
    BiochemicalAnalysisResponse,
    BiochemicalAnalysisUpdate,
    BiochemicalAnalysisValueCreate,
    BiochemicalAnalysisValueResponse,
    BiochemicalAnalysisValueUpdate,
    BiochemicalIndicatorCreate,
    BiochemicalIndicatorResponse,
    BiochemicalIndicatorUpdate,
    LaboratoryCreate,
    LaboratoryResponse,
    LaboratoryUpdate,
)
from src.features.biochemistry.service import (
    BiochemicalAnalysisService,
    BiochemicalAnalysisValueService,
    BiochemicalIndicatorService,
    LaboratoryService,
    get_biochemical_analysis_service,
    get_biochemical_analysis_value_service,
    get_biochemical_indicator_service,
    get_laboratory_service,
)
from src.shared.types import PyUUID

# ── Routers ────────────────────────────────────────────────────

laboratories_router = APIRouter(prefix="/laboratories", tags=["laboratories"])
indicators_router = APIRouter(
    prefix="/biochemical-indicators", tags=["biochemical-indicators"]
)
analyses_router = APIRouter(
    prefix="/biochemical-analyses", tags=["biochemical-analyses"]
)
values_router = APIRouter(
    prefix="/biochemical-analyses", tags=["biochemical-analysis-values"]
)


# ── Laboratory CRUD ────────────────────────────────────────────


@laboratories_router.get("/", response_model=list[LaboratoryResponse])
async def lab_list(
    service: Annotated[LaboratoryService, Depends(get_laboratory_service)],
):
    return await service.get_all()


@laboratories_router.get("/{id}", response_model=LaboratoryResponse)
async def lab_get(
    id: PyUUID,
    service: Annotated[LaboratoryService, Depends(get_laboratory_service)],
):
    return await service.get_one(id)


@laboratories_router.post("/", response_model=PyUUID, status_code=201)
async def lab_create(
    service: Annotated[LaboratoryService, Depends(get_laboratory_service)],
    item: LaboratoryCreate,
):
    return await service.create(item)


@laboratories_router.patch("/{id}", response_model=PyUUID)
async def lab_update(
    id: PyUUID,
    item: LaboratoryUpdate,
    service: Annotated[LaboratoryService, Depends(get_laboratory_service)],
):
    return await service.update(id, item)


@laboratories_router.delete("/{id}", status_code=204)
async def lab_delete(
    id: PyUUID,
    service: Annotated[LaboratoryService, Depends(get_laboratory_service)],
):
    await service.delete(id)


# ── BiochemicalIndicator CRUD ──────────────────────────────────


@indicators_router.get("/", response_model=list[BiochemicalIndicatorResponse])
async def indicator_list(
    service: Annotated[
        BiochemicalIndicatorService, Depends(get_biochemical_indicator_service)
    ],
):
    return await service.get_all()


@indicators_router.get("/{id}", response_model=BiochemicalIndicatorResponse)
async def indicator_get(
    id: PyUUID,
    service: Annotated[
        BiochemicalIndicatorService, Depends(get_biochemical_indicator_service)
    ],
):
    return await service.get_one(id)


@indicators_router.post("/", response_model=PyUUID, status_code=201)
async def indicator_create(
    service: Annotated[
        BiochemicalIndicatorService, Depends(get_biochemical_indicator_service)
    ],
    item: BiochemicalIndicatorCreate,
):
    return await service.create(item)


@indicators_router.patch("/{id}", response_model=PyUUID)
async def indicator_update(
    id: PyUUID,
    item: BiochemicalIndicatorUpdate,
    service: Annotated[
        BiochemicalIndicatorService, Depends(get_biochemical_indicator_service)
    ],
):
    return await service.update(id, item)


@indicators_router.delete("/{id}", status_code=204)
async def indicator_delete(
    id: PyUUID,
    service: Annotated[
        BiochemicalIndicatorService, Depends(get_biochemical_indicator_service)
    ],
):
    await service.delete(id)


# ── BiochemicalAnalysis CRUD ───────────────────────────────────


@analyses_router.get("/", response_model=list[BiochemicalAnalysisResponse])
async def analysis_list(
    service: Annotated[
        BiochemicalAnalysisService, Depends(get_biochemical_analysis_service)
    ],
):
    return await service.get_all()


@analyses_router.get("/{id}", response_model=BiochemicalAnalysisResponse)
async def analysis_get(
    id: PyUUID,
    service: Annotated[
        BiochemicalAnalysisService, Depends(get_biochemical_analysis_service)
    ],
):
    return await service.get_one(id)


@analyses_router.post("/", response_model=PyUUID, status_code=201)
async def analysis_create(
    service: Annotated[
        BiochemicalAnalysisService, Depends(get_biochemical_analysis_service)
    ],
    item: BiochemicalAnalysisCreate,
):
    return await service.create(item)


@analyses_router.patch("/{id}", response_model=PyUUID)
async def analysis_update(
    id: PyUUID,
    item: BiochemicalAnalysisUpdate,
    service: Annotated[
        BiochemicalAnalysisService, Depends(get_biochemical_analysis_service)
    ],
):
    return await service.update(id, item)


@analyses_router.delete("/{id}", status_code=204)
async def analysis_delete(
    id: PyUUID,
    service: Annotated[
        BiochemicalAnalysisService, Depends(get_biochemical_analysis_service)
    ],
):
    await service.delete(id)


# ── BiochemicalAnalysisValue endpoints ─────────────────────────


@values_router.get(
    "/{analysis_id}/values",
    response_model=list[BiochemicalAnalysisValueResponse],
)
async def value_list(
    analysis_id: PyUUID,
    service: Annotated[
        BiochemicalAnalysisValueService,
        Depends(get_biochemical_analysis_value_service),
    ],
):
    return await service.get_by_analysis_id(analysis_id)


@values_router.post(
    "/{analysis_id}/values",
    status_code=201,
)
async def value_create(
    analysis_id: PyUUID,
    item: BiochemicalAnalysisValueCreate,
    service: Annotated[
        BiochemicalAnalysisValueService,
        Depends(get_biochemical_analysis_value_service),
    ],
):
    await service.create(analysis_id, item)


@values_router.delete(
    "/{analysis_id}/values/{indicator_id}",
    status_code=204,
)
async def value_delete(
    analysis_id: PyUUID,
    indicator_id: PyUUID,
    service: Annotated[
        BiochemicalAnalysisValueService,
        Depends(get_biochemical_analysis_value_service),
    ],
):
    await service.delete(analysis_id, indicator_id)


@values_router.patch(
    "/{analysis_id}/values/{indicator_id}",
)
async def value_update(
    analysis_id: PyUUID,
    indicator_id: PyUUID,
    item: BiochemicalAnalysisValueUpdate,
    service: Annotated[
        BiochemicalAnalysisValueService,
        Depends(get_biochemical_analysis_value_service),
    ],
):
    await service.update(analysis_id, indicator_id, item)
