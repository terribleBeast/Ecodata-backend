from uuid import uuid4

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Genus(BaseSqlModel):
    __tablename__ = "genera"

    id: Mapped[PyUUID] = mapped_column(
        "genus_id", UUID, primary_key=True, default=uuid4
    )
    latin_name: Mapped[str] = mapped_column(String(150), unique=True)
    russian_name: Mapped[str | None] = mapped_column(String(150))


class Species(BaseSqlModel):
    __tablename__ = "species"
    __table_args__ = (UniqueConstraint("genus_id", "latin_name"),)

    id: Mapped[PyUUID] = mapped_column(
        "species_id", UUID, primary_key=True, default=uuid4
    )
    genus_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("genera.genus_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    latin_name: Mapped[str] = mapped_column(String(150))
    russian_name: Mapped[str | None] = mapped_column(String(150))

    genus: Mapped["Genus"] = relationship(lazy="joined")
