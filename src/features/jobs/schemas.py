from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID


class JobCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=150)]
    description: str | None = None


class JobUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=150)] = None
    description: str | None = None


class JobResponse(BaseSchema):
    job_id: PyUUID = Field(validation_alias="id")
    name: str
    description: str | None
