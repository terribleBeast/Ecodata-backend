from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID


class ResearcherNested(BaseSchema):
    researcher_id: PyUUID = Field(validation_alias="id")
    first_name: str
    last_name: str


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


class ResearchResponse(BaseSchema):
    research_id: PyUUID = Field(validation_alias="id")
    title: str
    goal: str | None
    description: str | None
    status: str
    start_date: date | None
    end_date: date | None
    created_by: ResearcherNested | None = None
    researcher_ids: list[ResearcherNested] = Field(
        default_factory=list,
        validation_alias="participants",
    )
    created_at: datetime
    updated_at: datetime


class ResearchAssignResearchers(BaseModel):
    researcher_ids: list[PyUUID]
