from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.types import PyUUID


class JobCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=150)]
    description: str | None = None


class JobUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=150)] = None
    description: str | None = None


class JobResponse(BaseModel):
    id: PyUUID
    name: str
    description: str | None
