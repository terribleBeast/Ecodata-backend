from typing import Annotated

from pydantic import BaseModel, Field
from src.features.locations.schemas import AddressNested
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID

# ── OrganizationType ──────────────────────────────────────────


class OrganizationTypeCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]


class OrganizationTypeUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None


class OrganizationTypeResponse(BaseSchema):
    organization_type_id: PyUUID = Field(validation_alias="id")
    name: str


class OrganizationTypeNested(BaseSchema):
    organization_type_id: PyUUID = Field(validation_alias="id")
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


class OrganizationResponse(BaseSchema):
    organization_id: PyUUID = Field(validation_alias="id")
    name: str
    organization_type: OrganizationTypeNested | None
    address: AddressNested | None
