from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import String
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Genus(BaseSqlModel):
    __tablename__ = "genera"

    id: Mapped[PyUUID] = mapped_column(
        "genus_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(40))


class Species(BaseSqlModel):
    __tablename__ = "species"

    id: Mapped[PyUUID] = mapped_column(
        "species_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(40))
    genus_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("genera.genus_id"),
    )
