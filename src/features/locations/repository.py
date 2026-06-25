from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.features.locations.models import (
    Address,
    Country,
    District,
    HouseNumber,
    Location,
    Region,
    Settlement,
    SettlementType,
    Street,
    StreetSettlementAssociation,
)
from src.shared.repository import SqlRepo


class CountryRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Country, session)


class RegionRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Region, session)

    async def get_all(self):
        stmt = select(self.model).options(selectinload(Region.country))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, id):
        stmt = (
            select(self.model)
            .options(selectinload(Region.country))
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class DistrictRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(District, session)

    async def get_all(self):
        stmt = select(self.model).options(selectinload(District.region))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, id):
        stmt = (
            select(self.model)
            .options(selectinload(District.region))
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class SettlementTypeRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(SettlementType, session)


class SettlementRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Settlement, session)

    async def get_all(self):
        stmt = select(self.model).options(
            selectinload(Settlement.district),
            selectinload(Settlement.settlement_type),
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, id):
        stmt = (
            select(self.model)
            .options(
                selectinload(Settlement.district),
                selectinload(Settlement.settlement_type),
            )
            .where(self.model.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class StreetRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Street, session)


class HouseNumberRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(HouseNumber, session)


class AddressRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Address, session)

    async def create(self, item: dict) -> None:
        # Creating an address requires the street–settlement pair to exist
        # in street_settlement_association. Ensure it exists first.
        stmt = select(StreetSettlementAssociation).where(
            StreetSettlementAssociation.street_id == item["street_id"],
            StreetSettlementAssociation.settlement_id == item["settlement_id"],
        )
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none() is None:
            await self.session.execute(
                insert(StreetSettlementAssociation).values(
                    street_id=item["street_id"],
                    settlement_id=item["settlement_id"],
                )
            )
        await super().create(item)


class LocationRepo(SqlRepo):
    def __init__(self, session: AsyncSession):
        super().__init__(Location, session)
