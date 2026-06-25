from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.features.research.models import Research
from src.features.researchers.models import Researcher
from src.shared.repository import SqlRepo
from src.shared.types import PyUUID


class ResearcherRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Researcher, session)

    async def get_by_ids(self, ids: list[PyUUID]):
        stmt = select(Researcher).filter(Researcher.id.in_(ids))

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def get_by_email(self, email: str) -> Researcher | None:
        stmt = (
            select(Researcher)
            .where(Researcher.email == email)
            .options(
                selectinload(Researcher.system_role),
                selectinload(Researcher.job),
                selectinload(Researcher.organization),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, id):
        stmt = (
            select(Researcher)
            .where(Researcher.id == id)
            .options(
                selectinload(Researcher.system_role),
                selectinload(Researcher.job),
                selectinload(Researcher.organization),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(Researcher).options(
            selectinload(Researcher.system_role),
            selectinload(Researcher.job),
            selectinload(Researcher.organization),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
