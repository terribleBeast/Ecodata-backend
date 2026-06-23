from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class NeuralModel(BaseSqlModel):
    __tablename__ = "neural_models"

    id: Mapped[PyUUID] = mapped_column(
        "neural_model_id", UUID, primary_key=True, default=uuid4
    )
    file_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("files.file_id", ondelete="RESTRICT"), unique=True
    )
    species_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("species.species_id", ondelete="SET NULL")
    )
    model_type: Mapped[str] = mapped_column(
        Enum(
            "species_classifier",
            "leaf_detector",
            "scaler",
            "morphology_extractor",
            "vein_segmenter",
            "scale_detector",
            name="model_type",
            create_type=False,
        )
    )
    input_format: Mapped[str | None] = mapped_column(Text)
    output_format: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )
