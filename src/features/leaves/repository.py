from sqlalchemy.ext.asyncio import AsyncSession
from src.features.leaves.models import Leaf, LeafArtifact
from src.shared.repository import SqlRepo


class LeafRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Leaf, session)


class LeafArtifactRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(LeafArtifact, session)
