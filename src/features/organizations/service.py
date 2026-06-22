from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.organizations.repository import OrganizationRepo, OrganizationTypeRepo
from src.shared.database import get_db
from src.shared.service import BaseService

# ── OrganizationType ──────────────────────────────────────────


async def get_organization_type_repo(
    session: AsyncSession = Depends(get_db),
) -> OrganizationTypeRepo:
    return OrganizationTypeRepo(session)


class OrganizationTypeService(BaseService[OrganizationTypeRepo]):
    def __init__(self, repo: OrganizationTypeRepo):
        self._repo = repo


async def get_organization_type_service(
    repo: OrganizationTypeRepo = Depends(get_organization_type_repo),
) -> OrganizationTypeService:
    return OrganizationTypeService(repo)


# ── Organization ──────────────────────────────────────────────


async def get_organization_repo(
    session: AsyncSession = Depends(get_db),
) -> OrganizationRepo:
    return OrganizationRepo(session)


class OrganizationService(BaseService[OrganizationRepo]):
    def __init__(self, repo: OrganizationRepo):
        self._repo = repo


async def get_organization_service(
    repo: OrganizationRepo = Depends(get_organization_repo),
) -> OrganizationService:
    return OrganizationService(repo)
