from pydantic import BaseModel
from src.shared.types import PyUUID


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


class NeuralModelResponse(BaseModel):
    id: PyUUID
    file_id: PyUUID
    species_id: PyUUID | None
    model_type: str
    input_format: str | None
    output_format: str | None
    is_active: bool


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
