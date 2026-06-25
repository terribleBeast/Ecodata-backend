from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID

# ── Geo hierarchy (top → bottom) ──────────────────────────────


class Country(BaseSqlModel):
    __tablename__ = "countries"

    id: Mapped[PyUUID] = mapped_column(
        "country_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True)


class Region(BaseSqlModel):
    __tablename__ = "regions"
    __table_args__ = (UniqueConstraint("country_id", "name"),)

    id: Mapped[PyUUID] = mapped_column(
        "region_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    country_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("countries.country_id", ondelete="RESTRICT")
    )

    country: Mapped["Country"] = relationship(lazy="joined")


class District(BaseSqlModel):
    __tablename__ = "districts"
    __table_args__ = (UniqueConstraint("region_id", "name"),)

    id: Mapped[PyUUID] = mapped_column(
        "district_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    region_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("regions.region_id", ondelete="RESTRICT")
    )

    region: Mapped["Region"] = relationship(lazy="joined")


class SettlementType(BaseSqlModel):
    __tablename__ = "settlement_types"

    id: Mapped[PyUUID] = mapped_column(
        "settlement_type_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255))


class Settlement(BaseSqlModel):
    __tablename__ = "settlements"
    __table_args__ = (UniqueConstraint("district_id", "settlement_type_id", "name"),)

    id: Mapped[PyUUID] = mapped_column(
        "settlement_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    district_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("districts.district_id", ondelete="RESTRICT")
    )
    settlement_type_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("settlement_types.settlement_type_id", ondelete="RESTRICT"),
    )

    district: Mapped["District"] = relationship(lazy="joined")
    settlement_type: Mapped["SettlementType"] = relationship(lazy="joined")


class Street(BaseSqlModel):
    __tablename__ = "streets"

    id: Mapped[PyUUID] = mapped_column(
        "street_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True)


class HouseNumber(BaseSqlModel):
    __tablename__ = "house_numbers"

    id: Mapped[PyUUID] = mapped_column(
        "house_number_id", UUID, primary_key=True, default=uuid4
    )
    number: Mapped[str] = mapped_column(String(50))


# ── Association & Address ─────────────────────────────────────


class StreetSettlementAssociation(BaseSqlModel):
    __tablename__ = "street_settlement_association"

    street_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("streets.street_id", ondelete="CASCADE"),
        primary_key=True,
    )
    settlement_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("settlements.settlement_id", ondelete="CASCADE"),
        primary_key=True,
    )


class Address(BaseSqlModel):
    __tablename__ = "addresses"
    __table_args__ = (
        UniqueConstraint("house_number_id", "street_id", "settlement_id"),
        ForeignKeyConstraint(
            ["street_id", "settlement_id"],
            [
                "street_settlement_association.street_id",
                "street_settlement_association.settlement_id",
            ],
            ondelete="RESTRICT",
        ),
    )

    id: Mapped[PyUUID] = mapped_column(
        "address_id", UUID, primary_key=True, default=uuid4
    )
    house_number_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("house_numbers.house_number_id", ondelete="RESTRICT")
    )
    street_id: Mapped[PyUUID] = mapped_column(UUID)
    settlement_id: Mapped[PyUUID] = mapped_column(UUID)


# ── Location ──────────────────────────────────────────────────


class Location(BaseSqlModel):
    __tablename__ = "locations"

    id: Mapped[PyUUID] = mapped_column(
        "location_id", UUID, primary_key=True, default=uuid4
    )
    address_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("addresses.address_id", ondelete="SET NULL")
    )
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )
