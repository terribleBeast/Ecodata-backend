from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.types import PyUUID

# ── OrganizationType ──────────────────────────────────────────


class OrganizationTypeCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]


class OrganizationTypeUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None


class OrganizationTypeResponse(BaseModel):
    id: PyUUID
    name: str


# ── Organization ──────────────────────────────────────────────


class OrganizationCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    organization_type_id: PyUUID | None = None
    address_id: PyUUID | None = None


class OrganizationUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    organization_type_id: PyUUID | None = None
    address_id: PyUUID | None = None


class OrganizationResponse(BaseModel):
    id: PyUUID
    name: str
    organization_type_id: PyUUID | None
    address_id: PyUUID | None
