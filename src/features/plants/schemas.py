from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID

# ── Nested schemas (used across response schemas) ───────────────


class SpeciesNested(BaseSchema):
    species_id: PyUUID = Field(validation_alias="id")
    latin_name: str
    russian_name: str | None


class PlantLifeFormNested(BaseSchema):
    plant_life_form_id: PyUUID = Field(validation_alias="id")
    name: str


class LeafBladeTypeNested(BaseSchema):
    leaf_blade_type_id: PyUUID = Field(validation_alias="id")
    name: str


class LocationNested(BaseSchema):
    location_id: PyUUID = Field(validation_alias="id")
    address_id: PyUUID | None
    latitude: Decimal | None
    longitude: Decimal | None
    description: str | None
    created_at: datetime


class PlantDescriptionNested(BaseSchema):
    plant_description_id: PyUUID = Field(validation_alias="id")
    species: SpeciesNested | None = None
    plant_life_form: PlantLifeFormNested
    leaf_blade_type: LeafBladeTypeNested
    description: str | None


# ── Plant ─────────────────────────────────────────────────────


class PlantCreate(BaseModel):
    location_id: PyUUID | None = None
    plant_description_id: PyUUID | None = None
    description: str | None = None


class PlantUpdate(BaseModel):
    location_id: PyUUID | None = None
    plant_description_id: PyUUID | None = None
    description: str | None = None


class PlantResponse(BaseSchema):
    plant_id: PyUUID = Field(validation_alias="id")
    location: LocationNested | None = None
    plant_description: PlantDescriptionNested | None = None
    description: str | None
    created_at: datetime


# ── PlantLifeForm ─────────────────────────────────────────────


class PlantLifeFormCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]


class PlantLifeFormUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None


class PlantLifeFormResponse(BaseSchema):
    plant_life_form_id: PyUUID = Field(validation_alias="id")
    name: str


# ── LeafBladeType ─────────────────────────────────────────────


class LeafBladeTypeCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]


class LeafBladeTypeUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None


class LeafBladeTypeResponse(BaseSchema):
    leaf_blade_type_id: PyUUID = Field(validation_alias="id")
    name: str


# ── PlantDescription ──────────────────────────────────────────


class PlantDescriptionCreate(BaseModel):
    species_id: PyUUID | None = None
    plant_life_form_id: PyUUID
    leaf_blade_type_id: PyUUID
    description: str | None = None


class PlantDescriptionUpdate(BaseModel):
    species_id: PyUUID | None = None
    plant_life_form_id: PyUUID | None = None
    leaf_blade_type_id: PyUUID | None = None
    description: str | None = None


class PlantDescriptionResponse(BaseSchema):
    plant_description_id: PyUUID = Field(validation_alias="id")
    species: SpeciesNested | None = None
    plant_life_form: PlantLifeFormNested
    leaf_blade_type: LeafBladeTypeNested
    description: str | None


# ── SideOfTheWorld ────────────────────────────────────────────


class SideOfTheWorldCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]


class SideOfTheWorldUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None


class SideOfTheWorldResponse(BaseSchema):
    side_of_the_world_id: PyUUID = Field(validation_alias="id")
    name: str


# ── LocationOnPlant ───────────────────────────────────────────


class LocationOnPlantCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]


class LocationOnPlantUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None


class LocationOnPlantResponse(BaseSchema):
    location_on_plant_id: PyUUID = Field(validation_alias="id")
    name: str
