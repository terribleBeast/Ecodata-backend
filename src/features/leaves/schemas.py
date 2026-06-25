from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID

# ── Nested schemas ─────────────────────────────────────────────


class PlantNested(BaseModel):
    plant_id: PyUUID = Field(validation_alias="id")
    description: str | None


class ImageNested(BaseModel):
    image_id: PyUUID = Field(validation_alias="id")
    width_px: int | None
    height_px: int | None
    image_type: str


class SideOfTheWorldNested(BaseModel):
    side_of_the_world_id: PyUUID = Field(validation_alias="id")
    name: str


class LocationOnPlantNested(BaseModel):
    location_on_plant_id: PyUUID = Field(validation_alias="id")
    name: str


class FileNested(BaseModel):
    file_id: PyUUID = Field(validation_alias="id")
    original_filename: str | None


class NeuralModelNested(BaseModel):
    neural_model_id: PyUUID = Field(validation_alias="id")
    model_type: str


class LeafNested(BaseModel):
    leaf_id: PyUUID = Field(validation_alias="id")
    leaf_index: int | None


# ── Create / Update / Response ─────────────────────────────────


class LeafCreate(BaseModel):
    plant_id: PyUUID
    image_id: PyUUID | None = None
    leaf_index: int | None = None
    side_of_the_world_id: PyUUID | None = None
    location_on_plant_id: PyUUID | None = None


class LeafUpdate(BaseModel):
    plant_id: PyUUID | None = None
    image_id: PyUUID | None = None
    leaf_index: int | None = None
    side_of_the_world_id: PyUUID | None = None
    location_on_plant_id: PyUUID | None = None


class LeafResponse(BaseModel):
    id: PyUUID
    plant: PlantNested
    image: ImageNested | None
    leaf_index: int | None
    side_of_the_world: SideOfTheWorldNested | None
    location_on_plant: LocationOnPlantNested | None
    created_at: datetime


class LeafArtifactCreate(BaseModel):
    leaf_id: PyUUID
    file_id: PyUUID
    artifact_type: str
    created_by_model_id: PyUUID | None = None


class LeafArtifactUpdate(BaseModel):
    leaf_id: PyUUID | None = None
    file_id: PyUUID | None = None
    artifact_type: str | None = None
    created_by_model_id: PyUUID | None = None


class LeafArtifactResponse(BaseModel):
    id: PyUUID
    leaf: LeafNested
    file: FileNested
    artifact_type: str
    created_by_model: NeuralModelNested | None
    created_at: datetime
