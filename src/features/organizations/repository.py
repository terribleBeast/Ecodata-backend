from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.features.organizations.models import Organization, OrganizationType
from src.shared.repository import SqlRepo


class OrganizationTypeRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(OrganizationType, session)


class OrganizationRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Organization, session)

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(Organization.organization_type),
            selectinload(Organization.address),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, id):
        stmt = (
            select(self.model)
            .options(
                selectinload(Organization.organization_type),
                selectinload(Organization.address),
            )
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
