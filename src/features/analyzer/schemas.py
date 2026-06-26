from datetime import datetime

from pydantic import BaseModel, Field
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID


class SpeciesNested(BaseSchema):
    species_id: PyUUID = Field(validation_alias="id")
    genus_id: PyUUID
    latin_name: str
    russian_name: str | None = None


class FileNested(BaseModel):
    file_id: PyUUID = Field(validation_alias="id")
    original_filename: str | None


class NeuralModelCreate(BaseModel):
    file_id: PyUUID
    species_id: PyUUID | None = None
    model_type: str = "species_classifier"
    input_format: str | None = None
    output_format: str | None = None


class NeuralModelUpdate(BaseModel):
    file_id: PyUUID | None = None
    species_id: PyUUID | None = None
    model_type: str | None = None
    input_format: str | None = None
    output_format: str | None = None
    is_active: bool | None = None


class NeuralModelResponse(BaseSchema):
    neural_model_id: PyUUID = Field(validation_alias="id")
    file: FileNested
    species: SpeciesNested | None
    model_type: str
    input_format: str | None
    output_format: str | None
    is_active: bool
    created_at: datetime


class Prediction(BaseModel):
    species: str
    probability: float


class BatchImageResult(BaseModel):
    index: int
    probabilities: dict[str, float]
    predicted: str


class BatchResultsResponse(BaseModel):
    total: int
    processed: int
    failed: int
    results: list[BatchImageResult]
