from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.types import PyUUID


class ResearcherCreate(BaseModel):
    user_id: PyUUID
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    patronymic: str | None = None
    phone: str | None = None
    orcid_link: Annotated[str | None, Field(max_length=20)] = None
    job_id: PyUUID | None = None
    organization_id: PyUUID | None = None


class ResearcherUpdate(BaseModel):
    first_name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    last_name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    patronymic: str | None = None
    phone: str | None = None
    orcid_link: Annotated[str | None, Field(max_length=20)] = None
    job_id: PyUUID | None = None
    organization_id: PyUUID | None = None


class ResearcherResponse(BaseModel):
    id: PyUUID
    user_id: PyUUID
    first_name: str
    last_name: str
    patronymic: str | None
    phone: str | None
    orcid_link: str | None
    job_id: PyUUID | None
    organization_id: PyUUID | None
