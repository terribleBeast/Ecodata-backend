from sqlalchemy.ext.asyncio import AsyncSession
from src.features.analyzer.models import NeuralModel
from src.shared.repository import SqlRepo
from src.shared.types import PyUUID


class NeuralModelRepo(SqlRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(NeuralModel, session)

    async def get_by_species(self, species_id: list[PyUUID]):
        return await self.search_by_field(field_name="species_id", value=species_id)
