from typing import Annotated

from fastapi import APIRouter, Depends
from src.features.auth.models import User
from src.features.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    SystemRoleCreate,
    SystemRoleResponse,
    SystemRoleUpdate,
    TokenResponse,
    UserResponse,
    UserUpdate,
)
from src.features.auth.service import (
    AuthService,
    SystemRoleService,
    UserService,
    get_auth_service,
    get_current_user,
    get_system_role_service,
    get_user_service,
)
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
        username=body.username,
        password=body.password,
        role_id=body.system_role_id,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
):
    return await auth.login(body.username, body.password)


@router.get("/me", response_model=UserResponse)
async def me(current_user: Annotated[User, Depends(get_current_user)]):
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


# ── Users (admin) ─────────────────────────────────────────────

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/", response_model=list[UserResponse])
async def user_list(
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.get_all()


@users_router.get("/{id}", response_model=UserResponse)
async def user_get(
    id: PyUUID,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.get_one(id)


@users_router.patch("/{id}", response_model=PyUUID)
async def user_update(
    id: PyUUID,
    item: UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.update(id, item)


@users_router.delete("/{id}", status_code=204)
async def user_delete(
    id: PyUUID,
    service: Annotated[UserService, Depends(get_user_service)],
):
    await service.delete(id)
