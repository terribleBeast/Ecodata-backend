from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class MeasurementUnit(BaseSqlModel):
    __tablename__ = "measurement_units"

    id: Mapped[PyUUID] = mapped_column(
        "measurement_unit_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100))
    symbol: Mapped[str] = mapped_column(String(30), unique=True)


class MorphologicalFeature(BaseSqlModel):
    __tablename__ = "morphological_features"

    id: Mapped[PyUUID] = mapped_column(
        "morphological_feature_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    default_unit_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("measurement_units.measurement_unit_id", ondelete="SET NULL"),
    )


class LeafMorphologicalFeatureValue(BaseSqlModel):
    __tablename__ = "leaf_morphological_feature_values"
    __table_args__ = (
        PrimaryKeyConstraint("leaf_id", "morphological_feature_id"),
        CheckConstraint("value >= 0", name="chk_morph_value"),
    )

    leaf_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("leaves.leaf_id", ondelete="CASCADE"),
        primary_key=True,
    )
    morphological_feature_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey(
            "morphological_features.morphological_feature_id", ondelete="RESTRICT"
        ),
        primary_key=True,
    )
    measurement_unit_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("measurement_units.measurement_unit_id", ondelete="SET NULL"),
    )
    value: Mapped[float] = mapped_column(Numeric(10, 4))
    measured_by_model_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("neural_models.neural_model_id", ondelete="SET NULL"),
    )
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )
