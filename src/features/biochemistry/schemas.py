from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.types import PyUUID

# ── Nested schemas ──────────────────────────────────────────────────


class OrganizationNested(BaseModel):
    organization_id: PyUUID = Field(validation_alias="id")
    name: str

    model_config = {"from_attributes": True}


class AddressNested(BaseModel):
    address_id: PyUUID = Field(validation_alias="id")

    model_config = {"from_attributes": True}


class MeasurementUnitNested(BaseModel):
    measurement_unit_id: PyUUID = Field(validation_alias="id")
    name: str
    symbol: str

    model_config = {"from_attributes": True}


class PlantNested(BaseModel):
    plant_id: PyUUID = Field(validation_alias="id")

    model_config = {"from_attributes": True}


class LabNested(BaseModel):
    laboratory_id: PyUUID = Field(validation_alias="id")
    name: str

    model_config = {"from_attributes": True}


class IndicatorNested(BaseModel):
    biochemical_indicator_id: PyUUID = Field(validation_alias="id")
    name: str

    model_config = {"from_attributes": True}


# ── Laboratory ─────────────────────────────────────────────────


class LaboratoryCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    organization_id: PyUUID | None = None
    address_id: PyUUID | None = None


class LaboratoryUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    organization_id: PyUUID | None = None
    address_id: PyUUID | None = None


class LaboratoryResponse(BaseModel):
    id: PyUUID
    name: str
    organization: OrganizationNested | None
    address: AddressNested | None

    model_config = {"from_attributes": True}


# ── BiochemicalIndicator ───────────────────────────────────────


class BiochemicalIndicatorCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=150)]
    description: str | None = None
    default_unit_id: PyUUID | None = None


class BiochemicalIndicatorUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=150)] = None
    description: str | None = None
    default_unit_id: PyUUID | None = None


class BiochemicalIndicatorResponse(BaseModel):
    id: PyUUID
    name: str
    description: str | None
    default_unit: MeasurementUnitNested | None

    model_config = {"from_attributes": True}


# ── BiochemicalAnalysis ────────────────────────────────────────


class BiochemicalAnalysisCreate(BaseModel):
    plant_id: PyUUID
    laboratory_id: PyUUID | None = None
    analysis_date: date | None = None
    comment: str | None = None


class BiochemicalAnalysisUpdate(BaseModel):
    plant_id: PyUUID | None = None
    laboratory_id: PyUUID | None = None
    analysis_date: date | None = None
    comment: str | None = None


class BiochemicalAnalysisResponse(BaseModel):
    id: PyUUID
    plant: PlantNested
    laboratory: LabNested | None
    analysis_date: date | None
    comment: str | None

    model_config = {"from_attributes": True}


# ── BiochemicalAnalysisValue ───────────────────────────────────


class BiochemicalAnalysisValueCreate(BaseModel):
    biochemical_indicator_id: PyUUID
    measurement_unit_id: PyUUID | None = None
    value: Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=4)]


class BiochemicalAnalysisValueUpdate(BaseModel):
    value: Annotated[Decimal | None, Field(ge=0, max_digits=10, decimal_places=4)] = (
        None
    )
    measurement_unit_id: PyUUID | None = None


class BiochemicalAnalysisValueResponse(BaseModel):
    biochemical_analysis_id: PyUUID
    indicator: IndicatorNested
    measurement_unit: MeasurementUnitNested | None
    value: Decimal

    model_config = {"from_attributes": True}
