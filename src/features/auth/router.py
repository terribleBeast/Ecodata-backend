from typing import Annotated

from fastapi import APIRouter, Depends
from src.features.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    ResearcherProfileResponse,
    SystemRoleCreate,
    SystemRoleResponse,
    SystemRoleUpdate,
    TokenResponse,
)
from src.features.auth.service import (
    AuthService,
    SystemRoleService,
    get_auth_service,
    get_current_user,
    get_system_role_service,
)
from src.features.researchers.models import Researcher
from src.shared.types import PyUUID

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Authentication ────────────────────────────────────────────


@router.post("/register", response_model=PyUUID, status_code=201)
async def register(
    body: RegisterRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
):
    return await auth.register(
        email=body.email,
        password=body.password,
        system_role_id=body.system_role_id,
        first_name=body.first_name,
        last_name=body.last_name,
        patronymic=body.patronymic,
        phone=body.phone,
        orcid_link=body.orcid_link,
        job_id=body.job_id,
        organization_id=body.organization_id,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
):
    return await auth.login(body.email, body.password)


@router.get("/me", response_model=ResearcherProfileResponse)
async def me(
    current_user: Annotated[Researcher, Depends(get_current_user)],
):
    return current_user


# ── System Roles ──────────────────────────────────────────────

roles_router = APIRouter(prefix="/roles", tags=["roles"])


@roles_router.get("/", response_model=list[SystemRoleResponse])
async def role_list(
    service: Annotated[SystemRoleService, Depends(get_system_role_service)],
):
    return await service.get_all()


@roles_router.get("/{id}", response_model=SystemRoleResponse)
async def role_get(
    id: PyUUID,
    service: Annotated[SystemRoleService, Depends(get_system_role_service)],
):
    return await service.get_one(id)


@roles_router.post("/", response_model=PyUUID, status_code=201)
async def role_create(
    item: SystemRoleCreate,
    service: Annotated[SystemRoleService, Depends(get_system_role_service)],
):
    return await service.create(item)


@roles_router.patch("/{id}", response_model=PyUUID)
async def role_update(
    id: PyUUID,
    item: SystemRoleUpdate,
    service: Annotated[SystemRoleService, Depends(get_system_role_service)],
):
    return await service.update(id, item)


@roles_router.delete("/{id}", status_code=204)
async def role_delete(
    id: PyUUID,
    service: Annotated[SystemRoleService, Depends(get_system_role_service)],
):
    await service.delete(id)
