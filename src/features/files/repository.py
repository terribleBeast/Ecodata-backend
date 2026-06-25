from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.features.files.models import File, Image
from src.shared.repository import SqlRepo


class FileRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(File, session)

    async def get_by_id(self, id):
        stmt = (
            select(self.model)
            .options(selectinload(File.uploaded_by))
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model).options(selectinload(File.uploaded_by))
        result = await self.session.execute(stmt)
        return result.scalars().all()


class ImageRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Image, session)

    async def get_by_id(self, id):
        stmt = (
            select(self.model)
            .options(
                selectinload(Image.file),
                selectinload(Image.uploaded_by),
            )
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(Image.file),
            selectinload(Image.uploaded_by),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
