from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.auth.repository import SystemRoleRepo
from src.features.auth.schemas import TokenResponse
from src.features.researchers.repository import ResearcherRepo
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


async def get_researcher_repo(
    session: AsyncSession = Depends(get_db),
) -> ResearcherRepo:
    return ResearcherRepo(session)


# ── Services ──────────────────────────────────────────────────


class SystemRoleService(BaseService[SystemRoleRepo]):
    def __init__(self, repo: SystemRoleRepo):
        self._repo = repo


class UserService(BaseService[ResearcherRepo]):
    def __init__(self, repo: ResearcherRepo):
        self._repo = repo


class AuthService:
    def __init__(self, researcher_repo: ResearcherRepo):
        self._researcher_repo = researcher_repo

    async def register(
        self,
        email: str,
        password: str,
        system_role_id: PyUUID,
        first_name: str,
        last_name: str,
        patronymic: str | None = None,
        phone: str | None = None,
        orcid_link: str | None = None,
        job_id: PyUUID | None = None,
        organization_id: PyUUID | None = None,
    ) -> PyUUID:
        existing = await self._researcher_repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

        researcher_id = self._researcher_repo.new_id()
        await self._researcher_repo.create(
            {
                "id": researcher_id,
                "email": email,
                "password_hash": hash_password(password),
                "system_role_id": system_role_id,
                "first_name": first_name,
                "last_name": last_name,
                "patronymic": patronymic,
                "phone": phone,
                "orcid_link": orcid_link,
                "job_id": job_id,
                "organization_id": organization_id,
            }
        )
        return researcher_id

    async def login(self, email: str, password: str) -> TokenResponse:
        researcher = await self._researcher_repo.get_by_email(email)
        if not researcher or not verify_password(password, researcher.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not researcher.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")

        token = create_access_token(
            {"sub": str(researcher.id), "email": researcher.email}
        )
        return TokenResponse(access_token=token)


# ── Dependency: current user ──────────────────────────────────


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    researcher_repo: ResearcherRepo = Depends(get_researcher_repo),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    researcher_id = payload.get("sub")
    if not isinstance(researcher_id, str):
        raise HTTPException(status_code=401, detail="Invalid token payload")
    researcher = await researcher_repo.get_by_id(PyUUID(researcher_id))
    if researcher is None or not researcher.is_active:
        raise HTTPException(status_code=401, detail="Researcher not found or inactive")
    return researcher


# ── Service factories ─────────────────────────────────────────


async def get_system_role_service(
    repo: SystemRoleRepo = Depends(get_system_role_repo),
) -> SystemRoleService:
    return SystemRoleService(repo)


async def get_user_service(
    repo: ResearcherRepo = Depends(get_researcher_repo),
) -> UserService:
    return UserService(repo)


async def get_auth_service(
    researcher_repo: ResearcherRepo = Depends(get_researcher_repo),
) -> AuthService:
    return AuthService(researcher_repo)
