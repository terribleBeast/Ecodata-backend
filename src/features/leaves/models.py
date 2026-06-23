from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Leaf(BaseSqlModel):
    __tablename__ = "leaves"

    id: Mapped[PyUUID] = mapped_column("leaf_id", UUID, primary_key=True, default=uuid4)
    plant_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("plants.plant_id", ondelete="CASCADE")
    )
    image_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("images.image_id", ondelete="SET NULL")
    )
    leaf_index: Mapped[int | None] = mapped_column(Integer)
    side_of_the_world_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("side_of_the_world.side_of_the_world_id", ondelete="SET NULL"),
    )
    location_on_plant_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("location_on_plant.location_on_plant_id", ondelete="SET NULL"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )


class LeafArtifact(BaseSqlModel):
    __tablename__ = "leaf_artifacts"

    id: Mapped[PyUUID] = mapped_column(
        "leaf_artifact_id", UUID, primary_key=True, default=uuid4
    )
    leaf_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("leaves.leaf_id", ondelete="CASCADE")
    )
    file_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("files.file_id", ondelete="RESTRICT")
    )
    artifact_type: Mapped[str] = mapped_column(
        Enum(
            "mask",
            "corrected_mask",
            "annotation_json",
            "visualisation",
            name="leaf_artifact_type",
            create_type=False,
        )
    )
    created_by_model_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("neural_models.neural_model_id", ondelete="SET NULL"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )
