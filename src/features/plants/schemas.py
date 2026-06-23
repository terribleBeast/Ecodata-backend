from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.types import PyUUID

# ── Plant ─────────────────────────────────────────────────────


class PlantCreate(BaseModel):
    location_id: PyUUID | None = None
    plant_description_id: PyUUID | None = None
    description: str | None = None


class PlantUpdate(BaseModel):
    location_id: PyUUID | None = None
    plant_description_id: PyUUID | None = None
    description: str | None = None


class PlantResponse(BaseModel):
    id: PyUUID
    location_id: PyUUID | None
    plant_description_id: PyUUID | None
    description: str | None


# ── PlantLifeForm ─────────────────────────────────────────────


class PlantLifeFormCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]


class PlantLifeFormUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None


class PlantLifeFormResponse(BaseModel):
    id: PyUUID
    name: str


# ── LeafBladeType ─────────────────────────────────────────────


class LeafBladeTypeCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]


class LeafBladeTypeUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None


class LeafBladeTypeResponse(BaseModel):
    id: PyUUID
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


class PlantDescriptionResponse(BaseModel):
    id: PyUUID
    species_id: PyUUID | None
    plant_life_form_id: PyUUID
    leaf_blade_type_id: PyUUID
    description: str | None


# ── SideOfTheWorld ────────────────────────────────────────────


class SideOfTheWorldCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]


class SideOfTheWorldUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None


class SideOfTheWorldResponse(BaseModel):
    id: PyUUID
    name: str


# ── LocationOnPlant ───────────────────────────────────────────


class LocationOnPlantCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]


class LocationOnPlantUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None


class LocationOnPlantResponse(BaseModel):
    id: PyUUID
    name: str
