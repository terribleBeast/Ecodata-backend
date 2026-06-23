from datetime import datetime

from pydantic import BaseModel
from src.shared.types import PyUUID


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
    plant_id: PyUUID
    image_id: PyUUID | None
    leaf_index: int | None
    side_of_the_world_id: PyUUID | None
    location_on_plant_id: PyUUID | None
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
    leaf_id: PyUUID
    file_id: PyUUID
    artifact_type: str
    created_by_model_id: PyUUID | None
    created_at: datetime
