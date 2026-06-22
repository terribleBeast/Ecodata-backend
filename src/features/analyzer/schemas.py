from pydantic import BaseModel
from src.shared.types import PyUUID


class NeuralModelCreate(BaseModel):
    name: str  # filename in storage
    species_id: PyUUID


class Prediction(BaseModel):
    species: str
    probability: float


class BatchImageResult(BaseModel):
    """Один результат в batch-ответе (REST или WebSocket)."""

    index: int
    probabilities: dict[str, float]
    predicted: str


class BatchResultsResponse(BaseModel):
    """Ответ batch-эндпоинта."""

    total: int
    processed: int
    failed: int
    results: list[BatchImageResult]
