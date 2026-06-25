from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID

# ── SystemRole ────────────────────────────────────────────────


class SystemRoleCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]


class SystemRoleUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None


class SystemRoleResponse(BaseSchema):
    system_role_id: PyUUID = Field(validation_alias="id")
    name: str


# ── Auth ──────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]
    system_role_id: PyUUID
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    patronymic: str | None = None
    phone: str | None = None
    orcid_link: Annotated[str | None, Field(max_length=20)] = None
    job_id: PyUUID | None = None
    organization_id: PyUUID | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Researcher profile (for /me) ──────────────────────────────


class JobNested(BaseSchema):
    job_id: PyUUID = Field(validation_alias="id")
    name: str


class SystemRoleNested(BaseSchema):
    system_role_id: PyUUID = Field(validation_alias="id")
    name: str


class OrganizationNested(BaseSchema):
    organization_id: PyUUID = Field(validation_alias="id")
    name: str


class ResearcherProfileResponse(BaseSchema):
    researcher_id: PyUUID = Field(validation_alias="id")
    email: str
    is_active: bool
    first_name: str
    last_name: str
    patronymic: str | None
    phone: str | None
    orcid_link: str | None
    created_at: datetime
    # joined
    system_role: SystemRoleNested | None = None
    job: JobNested | None = None
    organization: OrganizationNested | None = None
