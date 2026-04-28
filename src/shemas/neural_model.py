from pydantic.main import BaseModel

from src.database.models.plant import PyUUID


class NeuralModelCreate(BaseModel):
    plant_id: PyUUID
    model_name: str  # in storage
    # file of neural model
