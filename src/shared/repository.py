from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SqlRepo:
    """Generic base repository. Subclass and bind a model per feature."""

    def __init__(self, model, session: AsyncSession):
        self.session = session
        self.model = model

    @staticmethod
    def new_id() -> UUID:
        return uuid4()

    async def get_by_id(self, id: UUID):
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self):
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, item: dict[str, Any]) -> None:
        stmt = insert(self.model).values(**item)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update(self, id: UUID, changes: dict[str, Any]) -> None:
        stmt = update(self.model).where(self.model.id == id).values(**changes)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, id: UUID) -> None:
        stmt = delete(self.model).where(self.model.id == id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def search_by_field(
        self, field_name: str, value: Any | list[Any], exact_match: bool = True
    ):
        """Generic search by any field."""
        field = getattr(self.model, field_name, None)
        if field is None:
            raise ValueError(
                f"Field '{field_name}' does not exist on model {self.model.__name__}"
            )

        if exact_match:
            if isinstance(value, list):
                stmt = select(self.model).where(field.in_(value))
            else:
                stmt = select(self.model).where(field == value)
        else:
            stmt = select(self.model).where(field.ilike(f"%{value}%"))

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def join(self, foreign_key):
        stmt = select(self.model).join(foreign_key)
        result = await self.session.execute(stmt)
        return result.scalars().all()
