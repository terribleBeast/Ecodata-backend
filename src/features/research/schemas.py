from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.types import PyUUID


class ResearchCreate(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=255)]
    goal: str | None = None
    description: str | None = None
    status: Annotated[
        str, Field(default="draft", pattern=r"^(draft|active|completed|archived)$")
    ]
    start_date: date | None = None
    end_date: date | None = None
    created_by_researcher_id: PyUUID | None = None
    researcher_ids: list[PyUUID] = Field(default_factory=list)


class ResearchUpdate(BaseModel):
    title: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    goal: str | None = None
    description: str | None = None
    status: Annotated[
        str | None, Field(pattern=r"^(draft|active|completed|archived)$")
    ] = None
    start_date: date | None = None
    end_date: date | None = None
    researcher_ids: list[PyUUID] | None = None


class ResearchResponse(BaseModel):
    id: PyUUID
    title: str
    goal: str | None
    description: str | None
    status: str
    start_date: date | None
    end_date: date | None
    created_by_researcher_id: PyUUID | None


class ResearchAssignResearchers(BaseModel):
    researcher_ids: list[PyUUID]
