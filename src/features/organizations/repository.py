from sqlalchemy.ext.asyncio import AsyncSession
from src.features.organizations.models import Organization, OrganizationType
from src.shared.repository import SqlRepo


class OrganizationTypeRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(OrganizationType, session)


class OrganizationRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Organization, session)
