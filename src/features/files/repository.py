from sqlalchemy.ext.asyncio import AsyncSession
from src.features.files.models import File, Image
from src.shared.repository import SqlRepo


class FileRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(File, session)


class ImageRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Image, session)
