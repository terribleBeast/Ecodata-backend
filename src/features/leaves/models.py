from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Leaf(BaseSqlModel):
    __tablename__ = "leaves"
    __table_args__ = (UniqueConstraint("image_id", "leaf_index"),)

    id: Mapped[PyUUID] = mapped_column("leaf_id", UUID, primary_key=True, default=uuid4)
    plant_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("plants.plant_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    image_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("images.image_id", ondelete="SET NULL", onupdate="CASCADE")
    )
    leaf_index: Mapped[int | None] = mapped_column(Integer)
    side_of_the_world_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey(
            "side_of_the_world.side_of_the_world_id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )
    location_on_plant_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey(
            "location_on_plant.location_on_plant_id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        nullable=False,
    )

    plant: Mapped["Plant"] = relationship(lazy="joined")
    image: Mapped["Image | None"] = relationship(lazy="joined")
    side_of_the_world: Mapped["SideOfTheWorld | None"] = relationship(lazy="joined")
    location_on_plant: Mapped["LocationOnPlant | None"] = relationship(lazy="joined")


class LeafArtifact(BaseSqlModel):
    __tablename__ = "leaf_artifacts"
    __table_args__ = (UniqueConstraint("leaf_id", "artifact_type", "file_id"),)

    id: Mapped[PyUUID] = mapped_column(
        "leaf_artifact_id", UUID, primary_key=True, default=uuid4
    )
    leaf_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("leaves.leaf_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    file_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("files.file_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    artifact_type: Mapped[str] = mapped_column(
        Enum(
            "mask",
            "corrected_mask",
            "annotation_json",
            "visualisation",
            name="leaf_artifact_type",
            create_type=False,
        ),
        nullable=False,
    )
    created_by_model_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey(
            "neural_models.neural_model_id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        nullable=False,
    )

    leaf: Mapped["Leaf"] = relationship(lazy="joined")
    file: Mapped["File"] = relationship(lazy="joined")
    created_by_model: Mapped["NeuralModel | None"] = relationship(
        lazy="joined", foreign_keys=[created_by_model_id]
    )


from src.features.analyzer.models import NeuralModel  # noqa: E402, F401
from src.features.files.models import File, Image  # noqa: E402, F401
from src.features.plants.models import (  # noqa: E402, F401
    LocationOnPlant,
    Plant,
    SideOfTheWorld,
)
