from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.taxonomy.models import Genus, Species
from src.shared.repository import SqlRepo
from src.shared.types import PyUUID


class GenusRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Genus, session)

    async def search_by_name(self, name: str, exact: bool = False):
        return await self.search_by_field("name", name, exact_match=exact)


class SpeciesRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Species, session)

    async def get_by_genus(self, genus_id: PyUUID):
        return await self.search_by_field("genus_id", genus_id)

    async def search_by_name(self, name: str, exact: bool = False):
        return await self.search_by_field("name", name, exact_match=exact)

    async def get_with_genus(self, species_id):
        """Return species with joined genus data."""
        stmt = (
            select(Species, Genus)
            .join(Genus, Species.genus_id == Genus.id)
            .where(Species.id == species_id)
        )
        result = await self.session.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        species, genus = row
        return species, genus
