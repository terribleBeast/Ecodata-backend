from typing import Annotated

from fastapi import APIRouter, Depends, status
from src.features.morphology.schemas import (
    LeafMorphologicalFeatureValueCreate,
    LeafMorphologicalFeatureValueRead,
    LeafMorphologicalFeatureValueUpdate,
    MeasurementUnitCreate,
    MeasurementUnitRead,
    MeasurementUnitUpdate,
    MorphologicalFeatureCreate,
    MorphologicalFeatureRead,
    MorphologicalFeatureUpdate,
)
from src.features.morphology.service import (
    LeafMorphologicalFeatureValueService,
    MeasurementUnitService,
    MorphologicalFeatureService,
    get_leaf_morphological_feature_value_service,
    get_measurement_unit_service,
    get_morphological_feature_service,
)
from src.shared.types import PyUUID

# ── Measurement Units ──────────────────────────────────────────────

measurement_units_router = APIRouter(
    prefix="/measurement-units", tags=["measurement-units"]
)


@measurement_units_router.get("/", response_model=list[MeasurementUnitRead])
async def measurement_unit_list(
    service: Annotated[MeasurementUnitService, Depends(get_measurement_unit_service)],
    q: str | None = None,
):
    if q:
        return await service.search_by_field("name", q)
    return await service.get_all()


@measurement_units_router.get("/{id}", response_model=MeasurementUnitRead)
async def measurement_unit_get(
    id: PyUUID,
    service: Annotated[MeasurementUnitService, Depends(get_measurement_unit_service)],
):
    return await service.get_one(id)


@measurement_units_router.post(
    "/",
    response_model=MeasurementUnitRead,
    status_code=status.HTTP_201_CREATED,
)
async def measurement_unit_create(
    service: Annotated[MeasurementUnitService, Depends(get_measurement_unit_service)],
    body: MeasurementUnitCreate,
):
    item = await service.get_one(await service.create(body))
    return item


@measurement_units_router.put("/{id}", response_model=MeasurementUnitRead)
async def measurement_unit_update(
    id: PyUUID,
    body: MeasurementUnitUpdate,
    service: Annotated[MeasurementUnitService, Depends(get_measurement_unit_service)],
):
    await service.update(id, body)
    return await service.get_one(id)


@measurement_units_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def measurement_unit_delete(
    id: PyUUID,
    service: Annotated[MeasurementUnitService, Depends(get_measurement_unit_service)],
):
    await service.delete(id)


# ── Morphological Features ─────────────────────────────────────────

morphological_features_router = APIRouter(
    prefix="/morphological-features", tags=["morphological-features"]
)


@morphological_features_router.get("/", response_model=list[MorphologicalFeatureRead])
async def morphological_feature_list(
    service: Annotated[
        MorphologicalFeatureService, Depends(get_morphological_feature_service)
    ],
    q: str | None = None,
):
    if q:
        return await service.search_by_field("name", q)
    return await service.get_all()


@morphological_features_router.get("/{id}", response_model=MorphologicalFeatureRead)
async def morphological_feature_get(
    id: PyUUID,
    service: Annotated[
        MorphologicalFeatureService, Depends(get_morphological_feature_service)
    ],
):
    return await service.get_one(id)


@morphological_features_router.post(
    "/",
    response_model=MorphologicalFeatureRead,
    status_code=status.HTTP_201_CREATED,
)
async def morphological_feature_create(
    service: Annotated[
        MorphologicalFeatureService, Depends(get_morphological_feature_service)
    ],
    body: MorphologicalFeatureCreate,
):
    item = await service.get_one(await service.create(body))
    return item


@morphological_features_router.put("/{id}", response_model=MorphologicalFeatureRead)
async def morphological_feature_update(
    id: PyUUID,
    body: MorphologicalFeatureUpdate,
    service: Annotated[
        MorphologicalFeatureService, Depends(get_morphological_feature_service)
    ],
):
    await service.update(id, body)
    return await service.get_one(id)


@morphological_features_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def morphological_feature_delete(
    id: PyUUID,
    service: Annotated[
        MorphologicalFeatureService, Depends(get_morphological_feature_service)
    ],
):
    await service.delete(id)


# ── Leaf Morphological Feature Values ──────────────────────────────

leaf_morph_values_router = APIRouter(
    prefix="/leaf-morphological-feature-values",
    tags=["leaf-morphological-feature-values"],
)


@leaf_morph_values_router.get(
    "/", response_model=list[LeafMorphologicalFeatureValueRead]
)
async def leaf_morph_value_list(
    service: Annotated[
        LeafMorphologicalFeatureValueService,
        Depends(get_leaf_morphological_feature_value_service),
    ],
):
    return await service.get_all()


@leaf_morph_values_router.post(
    "/",
    response_model=LeafMorphologicalFeatureValueRead,
    status_code=status.HTTP_201_CREATED,
)
async def leaf_morph_value_create(
    service: Annotated[
        LeafMorphologicalFeatureValueService,
        Depends(get_leaf_morphological_feature_value_service),
    ],
    body: LeafMorphologicalFeatureValueCreate,
):
    await service.create(body)
    return await service.get_one(body.leaf_id, body.morphological_feature_id)


@leaf_morph_values_router.patch(
    "/{leaf_id}/{morphological_feature_id}",
    response_model=LeafMorphologicalFeatureValueRead,
)
async def leaf_morph_value_update(
    leaf_id: PyUUID,
    morphological_feature_id: PyUUID,
    body: LeafMorphologicalFeatureValueUpdate,
    service: Annotated[
        LeafMorphologicalFeatureValueService,
        Depends(get_leaf_morphological_feature_value_service),
    ],
):
    await service.update_value(leaf_id, morphological_feature_id, body)
    return await service.get_one(leaf_id, morphological_feature_id)


@leaf_morph_values_router.delete(
    "/{leaf_id}/{morphological_feature_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def leaf_morph_value_delete(
    leaf_id: PyUUID,
    morphological_feature_id: PyUUID,
    service: Annotated[
        LeafMorphologicalFeatureValueService,
        Depends(get_leaf_morphological_feature_value_service),
    ],
):
    await service.delete(leaf_id, morphological_feature_id)
