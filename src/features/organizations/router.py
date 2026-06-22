from typing import Annotated

from fastapi import APIRouter, Depends
from src.features.organizations.schemas import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationTypeCreate,
    OrganizationTypeResponse,
    OrganizationTypeUpdate,
    OrganizationUpdate,
)
from src.features.organizations.service import (
    OrganizationService,
    OrganizationTypeService,
    get_organization_service,
    get_organization_type_service,
)
from src.shared.types import PyUUID

router = APIRouter(prefix="/organizations", tags=["organizations"])

# ── Sub-router for organization-types ─────────────────────────

org_type_router = APIRouter(prefix="/organizations/types", tags=["organization-types"])


@org_type_router.get("/", response_model=list[OrganizationTypeResponse])
async def org_type_list(
    service: Annotated[OrganizationTypeService, Depends(get_organization_type_service)],
):
    return await service.get_all()


@org_type_router.get("/{id}", response_model=OrganizationTypeResponse)
async def org_type_get(
    id: PyUUID,
    service: Annotated[OrganizationTypeService, Depends(get_organization_type_service)],
):
    return await service.get_one(id)


@org_type_router.post("/", response_model=PyUUID, status_code=201)
async def org_type_create(
    service: Annotated[OrganizationTypeService, Depends(get_organization_type_service)],
    item: OrganizationTypeCreate,
):
    return await service.create(item)


@org_type_router.patch("/{id}", response_model=PyUUID)
async def org_type_update(
    id: PyUUID,
    item: OrganizationTypeUpdate,
    service: Annotated[OrganizationTypeService, Depends(get_organization_type_service)],
):
    return await service.update(id, item)


@org_type_router.delete("/{id}", status_code=204)
async def org_type_delete(
    id: PyUUID,
    service: Annotated[OrganizationTypeService, Depends(get_organization_type_service)],
):
    await service.delete(id)


# ── Organization CRUD ─────────────────────────────────────────


@router.get("/", response_model=list[OrganizationResponse])
async def org_list(
    service: Annotated[OrganizationService, Depends(get_organization_service)],
):
    return await service.get_all()


@router.get("/{id}", response_model=OrganizationResponse)
async def org_get(
    id: PyUUID,
    service: Annotated[OrganizationService, Depends(get_organization_service)],
):
    return await service.get_one(id)


@router.post("/", response_model=PyUUID, status_code=201)
async def org_create(
    service: Annotated[OrganizationService, Depends(get_organization_service)],
    item: OrganizationCreate,
):
    return await service.create(item)


@router.patch("/{id}", response_model=PyUUID)
async def org_update(
    id: PyUUID,
    item: OrganizationUpdate,
    service: Annotated[OrganizationService, Depends(get_organization_service)],
):
    return await service.update(id, item)


@router.delete("/{id}", status_code=204)
async def org_delete(
    id: PyUUID,
    service: Annotated[OrganizationService, Depends(get_organization_service)],
):
    await service.delete(id)
