from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.types import PyUUID

# ── MeasurementUnit ────────────────────────────────────────────────


class MeasurementUnitCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    symbol: Annotated[str, Field(min_length=1, max_length=30)]


class MeasurementUnitUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    symbol: Annotated[str | None, Field(min_length=1, max_length=30)] = None


class MeasurementUnitRead(BaseModel):
    id: PyUUID
    name: str
    symbol: str

    model_config = {"from_attributes": True}


# ── MorphologicalFeature ───────────────────────────────────────────


class MorphologicalFeatureCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=150)]
    description: str | None = None
    default_unit_id: PyUUID | None = None


class MorphologicalFeatureUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=150)] = None
    description: str | None = None
    default_unit_id: PyUUID | None = None


class MorphologicalFeatureRead(BaseModel):
    id: PyUUID
    name: str
    description: str | None
    default_unit_id: PyUUID | None

    model_config = {"from_attributes": True}


# ── LeafMorphologicalFeatureValue ──────────────────────────────────


class LeafMorphologicalFeatureValueCreate(BaseModel):
    leaf_id: PyUUID
    morphological_feature_id: PyUUID
    measurement_unit_id: PyUUID | None = None
    value: Decimal
    measured_by_model_id: PyUUID | None = None


class LeafMorphologicalFeatureValueUpdate(BaseModel):
    measurement_unit_id: PyUUID | None = None
    value: Decimal | None = None
    measured_by_model_id: PyUUID | None = None


class LeafMorphologicalFeatureValueRead(BaseModel):
    leaf_id: PyUUID
    morphological_feature_id: PyUUID
    measurement_unit_id: PyUUID | None
    value: Decimal
    measured_by_model_id: PyUUID | None
    measured_at: datetime

    model_config = {"from_attributes": True}
