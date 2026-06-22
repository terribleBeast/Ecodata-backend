from typing import Annotated

from pydantic import BaseModel, EmailStr, Field
from src.shared.types import PyUUID

# ── SystemRole ────────────────────────────────────────────────


class SystemRoleCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]


class SystemRoleUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None


class SystemRoleResponse(BaseModel):
    id: PyUUID
    name: str


# ── Auth ──────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=100)]
    password: Annotated[str, Field(min_length=8, max_length=128)]
    system_role_id: PyUUID


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── User ──────────────────────────────────────────────────────


class UserResponse(BaseModel):
    id: PyUUID
    email: str
    username: str
    system_role_id: PyUUID
    is_active: bool


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: Annotated[str | None, Field(min_length=3, max_length=100)] = None
    password: Annotated[str | None, Field(min_length=8, max_length=128)] = None
    system_role_id: PyUUID | None = None
    is_active: bool | None = None
