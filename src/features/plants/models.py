from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Plant(BaseSqlModel):
    __tablename__ = "plants"

    id: Mapped[PyUUID] = mapped_column(
        "plant_id", UUID, primary_key=True, default=uuid4
    )
    location_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("locations.location_id", ondelete="SET NULL")
    )
    plant_description_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("plant_descriptions.plant_description_id", ondelete="SET NULL"),
    )
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )


class PlantLifeForm(BaseSqlModel):
    __tablename__ = "plant_life_forms"

    id: Mapped[PyUUID] = mapped_column(
        "plant_life_form_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255))


class LeafBladeType(BaseSqlModel):
    __tablename__ = "leaf_blade_types"

    id: Mapped[PyUUID] = mapped_column(
        "leaf_blade_type_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255))


class PlantDescription(BaseSqlModel):
    __tablename__ = "plant_descriptions"

    id: Mapped[PyUUID] = mapped_column(
        "plant_description_id", UUID, primary_key=True, default=uuid4
    )
    species_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("species.species_id", ondelete="SET NULL")
    )
    plant_life_form_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("plant_life_forms.plant_life_form_id", ondelete="RESTRICT"),
    )
    leaf_blade_type_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("leaf_blade_types.leaf_blade_type_id", ondelete="RESTRICT"),
    )
    description: Mapped[str | None] = mapped_column(Text)


class SideOfTheWorld(BaseSqlModel):
    __tablename__ = "side_of_the_world"

    id: Mapped[PyUUID] = mapped_column(
        "side_of_the_world_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True)


class LocationOnPlant(BaseSqlModel):
    __tablename__ = "location_on_plant"

    id: Mapped[PyUUID] = mapped_column(
        "location_on_plant_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True)
