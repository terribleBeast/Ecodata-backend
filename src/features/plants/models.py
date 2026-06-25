from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Plant(BaseSqlModel):
    __tablename__ = "plants"

    id: Mapped[PyUUID] = mapped_column(
        "plant_id", UUID, primary_key=True, default=uuid4
    )
    location_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("locations.location_id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    plant_description_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey(
            "plant_descriptions.plant_description_id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        nullable=False,
    )

    location: Mapped["Location | None"] = relationship(lazy="joined")
    plant_description: Mapped["PlantDescription | None"] = relationship(lazy="joined")


class PlantLifeForm(BaseSqlModel):
    __tablename__ = "plant_life_forms"

    id: Mapped[PyUUID] = mapped_column(
        "plant_life_form_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class LeafBladeType(BaseSqlModel):
    __tablename__ = "leaf_blade_types"

    id: Mapped[PyUUID] = mapped_column(
        "leaf_blade_type_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class PlantDescription(BaseSqlModel):
    __tablename__ = "plant_descriptions"

    id: Mapped[PyUUID] = mapped_column(
        "plant_description_id", UUID, primary_key=True, default=uuid4
    )
    species_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("species.species_id", ondelete="SET NULL", onupdate="CASCADE")
    )
    plant_life_form_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey(
            "plant_life_forms.plant_life_form_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    leaf_blade_type_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey(
            "leaf_blade_types.leaf_blade_type_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)

    species: Mapped["Species | None"] = relationship(lazy="joined")
    plant_life_form: Mapped["PlantLifeForm"] = relationship(lazy="joined")
    leaf_blade_type: Mapped["LeafBladeType"] = relationship(lazy="joined")


class SideOfTheWorld(BaseSqlModel):
    __tablename__ = "side_of_the_world"

    id: Mapped[PyUUID] = mapped_column(
        "side_of_the_world_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class LocationOnPlant(BaseSqlModel):
    __tablename__ = "location_on_plant"

    id: Mapped[PyUUID] = mapped_column(
        "location_on_plant_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


# ── Circular imports (cross-feature references) ────────────────

from src.features.locations.models import Location  # noqa: E402
from src.features.taxonomy.models import Species  # noqa: E402
