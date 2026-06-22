from pydantic import BaseModel
from src.shared.types import PyUUID


class ResearchCreate(BaseModel):
    title: str
    goal: str
    researchers_id: list[PyUUID]
