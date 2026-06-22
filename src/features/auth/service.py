from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.auth.repository import SystemRoleRepo, UserRepo
from src.features.auth.schemas import TokenResponse
from src.shared.database import get_db
from src.shared.service import BaseService
from src.shared.types import PyUUID

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

_password_hasher = PasswordHash.recommended()
_bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    return _password_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_hasher.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ── Repo factories ────────────────────────────────────────────


async def get_system_role_repo(
    session: AsyncSession = Depends(get_db),
) -> SystemRoleRepo:
    return SystemRoleRepo(session)


async def get_user_repo(
    session: AsyncSession = Depends(get_db),
) -> UserRepo:
    return UserRepo(session)


# ── Services ──────────────────────────────────────────────────


class SystemRoleService(BaseService[SystemRoleRepo]):
    def __init__(self, repo: SystemRoleRepo):
        self._repo = repo


class UserService(BaseService[UserRepo]):
    def __init__(self, repo: UserRepo):
        self._repo = repo


class AuthService:
    def __init__(self, user_repo: UserRepo):
        self._user_repo = user_repo

    async def register(
        self, email: str, username: str, password: str, role_id: PyUUID
    ) -> PyUUID:
        existing = await self._user_repo.get_by_username(username)
        if existing:
            raise HTTPException(status_code=409, detail="Username already taken")
        existing = await self._user_repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

        user_id = self._user_repo.new_id()
        await self._user_repo.create(
            {
                "id": user_id,
                "email": email,
                "username": username,
                "password_hash": hash_password(password),
                "system_role_id": role_id,
            }
        )
        return user_id

    async def login(self, username: str, password: str) -> TokenResponse:
        user = await self._user_repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")

        token = create_access_token({"sub": str(user.id), "username": user.username})
        return TokenResponse(access_token=token)


# ── Dependency: current user ──────────────────────────────────


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    user_repo: UserRepo = Depends(get_user_repo),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = await user_repo.get_by_id(PyUUID(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


# ── Service factories ─────────────────────────────────────────


async def get_system_role_service(
    repo: SystemRoleRepo = Depends(get_system_role_repo),
) -> SystemRoleService:
    return SystemRoleService(repo)


async def get_user_service(
    repo: UserRepo = Depends(get_user_repo),
) -> UserService:
    return UserService(repo)


async def get_auth_service(
    user_repo: UserRepo = Depends(get_user_repo),
) -> AuthService:
    return AuthService(user_repo)
