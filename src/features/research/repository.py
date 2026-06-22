from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.research.models import Research, ResearcherResearchAssociation
from src.shared.repository import SqlRepo
from src.shared.types import PyUUID


class ResearchRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Research, session)

    async def search_by_status(self, status: str) -> list[Research]:
        stmt = select(Research).where(Research.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_researchers(
        self, research_id: PyUUID, researcher_ids: list[PyUUID]
    ) -> None:
        values = [
            {"research_id": research_id, "researcher_id": rid} for rid in researcher_ids
        ]
        stmt = insert(ResearcherResearchAssociation).values(values)
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_researchers(
        self, research_id: PyUUID, researcher_ids: list[PyUUID]
    ) -> None:
        stmt = delete(ResearcherResearchAssociation).where(
            ResearcherResearchAssociation.research_id == research_id,
            ResearcherResearchAssociation.researcher_id.in_(researcher_ids),
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def set_researchers(
        self, research_id: PyUUID, researcher_ids: list[PyUUID]
    ) -> None:
        # replace the whole set atomically
        async with self.session.begin():
            await self.session.execute(
                delete(ResearcherResearchAssociation).where(
                    ResearcherResearchAssociation.research_id == research_id
                )
            )
            if researcher_ids:
                values = [
                    {"research_id": research_id, "researcher_id": rid}
                    for rid in researcher_ids
                ]
                await self.session.execute(
                    insert(ResearcherResearchAssociation).values(values)
                )
