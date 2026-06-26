from datetime import datetime
from typing import Annotated

from pydantic import AliasChoices, BaseModel, Field
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID

# ── Nested (joined) ─────────────────────────────────────────


class JobNested(BaseSchema):
    job_id: PyUUID = Field(validation_alias="id")
    name: str


class SystemRoleNested(BaseSchema):
    system_role_id: PyUUID = Field(validation_alias="id")
    name: str


class OrganizationNested(BaseSchema):
    organization_id: PyUUID = Field(validation_alias="id")
    name: str


# ── Researcher ──────────────────────────────────────────────


class ResearcherCreate(BaseModel):
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


class ResearcherResponse(BaseSchema):
    id: PyUUID = Field(validation_alias=AliasChoices("id", "researcher_id"))
    email: str
    is_active: bool
    first_name: str
    last_name: str
    patronymic: str | None
    phone: str | None
    orcid_link: str | None
    created_at: datetime
    # joined — readable names, not raw IDs
    system_role: SystemRoleNested | None = None
    job: JobNested | None = None
    organization: OrganizationNested | None = None
