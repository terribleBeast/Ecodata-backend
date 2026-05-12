from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SqlRepo:
    def __init__(self, model, session: AsyncSession):
        """Session should be passed in, not created internally"""
        self.session = session
        self.model = model

    @staticmethod
    def new_id() -> UUID:
        return uuid4()

    async def get_by_id(self, id: int):
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def get_all(self):
        try:
            stmt = select(self.model)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def create(self, item: dict[str, Any]) -> None:
        try:
            stmt = insert(self.model).values(**item)
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def update(self, id: UUID, changes: dict[str, Any]) -> None:
        try:
            stmt = update(self.model).where(self.model.id == id).values(**changes)
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def delete(self, id: UUID) -> None:
        try:
            stmt = delete(self.model).where(self.model.id == id)
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def search_by_field(
        self, field_name: str, value: Any, exact_match: bool = True
    ):
        """Generic search by any field"""
        try:
            field = getattr(self.model, field_name, None)
            if field is None:
                raise ValueError(
                    f"Field '{field_name}' does not exist on model {self.model.__name__}"
                )

            if exact_match:
                stmt = select(self.model).where(field == value)
            else:
                # Case-insensitive partial match
                stmt = select(self.model).where(field.ilike(f"%{value}%"))

            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e


class PlantRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        from src.database.models.plant import Plant

        super().__init__(Plant, session)

    async def select_by_genus(self, genus: str):
        try:
            stmt = select(self.model).where(self.model.c.genus == genus)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e


class NeuralModelRepo(SqlRepo):
    def __init__(self, session: AsyncSession) -> None:
        from src.database.models.neural_models import NeuralModel

        super().__init__(NeuralModel, session)
