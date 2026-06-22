from sqlalchemy.ext.asyncio import AsyncSession
from src.features.plants.models import Plant
from src.shared.repository import SqlRepo


class PlantRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Plant, session)

    async def select_by_genus(self, genus: str):
        return await self.search_by_field(field_name="genus", value=genus)
