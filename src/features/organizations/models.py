from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.features.locations.models import Address
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class OrganizationType(BaseSqlModel):
    __tablename__ = "organization_types"

    id: Mapped[PyUUID] = mapped_column(
        "organization_type_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True)


class Organization(BaseSqlModel):
    __tablename__ = "organizations"

    id: Mapped[PyUUID] = mapped_column(
        "organization_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255))
    organization_type_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("organization_types.organization_type_id", ondelete="SET NULL")
    )
    address_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("addresses.address_id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )

    organization_type: Mapped["OrganizationType | None"] = relationship(lazy="joined")
    address: Mapped["Address | None"] = relationship(lazy="joined")
