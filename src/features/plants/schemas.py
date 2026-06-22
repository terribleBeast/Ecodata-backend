from pydantic import BaseModel
from src.shared.types import PyUUID


class PlantCreate(BaseModel):
    name: str
    species_id: PyUUID
