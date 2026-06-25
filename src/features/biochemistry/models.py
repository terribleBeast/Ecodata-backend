from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID

# ── Laboratory ─────────────────────────────────────────────────


class Laboratory(BaseSqlModel):
    __tablename__ = "laboratories"

    id: Mapped[PyUUID] = mapped_column(
        "laboratory_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    organization_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("organizations.organization_id", ondelete="SET NULL")
    )
    address_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("addresses.address_id", ondelete="SET NULL")
    )

    organization: Mapped["Organization | None"] = relationship(
        "Organization", lazy="joined"
    )
    address: Mapped["Address | None"] = relationship("Address", lazy="joined")


# ── BiochemicalIndicator ───────────────────────────────────────


class BiochemicalIndicator(BaseSqlModel):
    __tablename__ = "biochemical_indicators"

    id: Mapped[PyUUID] = mapped_column(
        "biochemical_indicator_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    default_unit_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("measurement_units.measurement_unit_id", ondelete="SET NULL"),
    )

    default_unit: Mapped["MeasurementUnit | None"] = relationship(
        "MeasurementUnit", lazy="joined"
    )


# ── BiochemicalAnalysis ────────────────────────────────────────


class BiochemicalAnalysis(BaseSqlModel):
    __tablename__ = "biochemical_analyses"

    id: Mapped[PyUUID] = mapped_column(
        "biochemical_analysis_id", UUID, primary_key=True, default=uuid4
    )
    plant_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("plants.plant_id", ondelete="CASCADE")
    )
    laboratory_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("laboratories.laboratory_id", ondelete="SET NULL")
    )
    analysis_date: Mapped[date | None] = mapped_column(Date)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )

    plant: Mapped["Plant"] = relationship("Plant", lazy="joined")
    laboratory: Mapped["Laboratory | None"] = relationship("Laboratory", lazy="joined")


# ── BiochemicalAnalysisValue ───────────────────────────────────


class BiochemicalAnalysisValue(BaseSqlModel):
    __tablename__ = "biochemical_analysis_values"

    biochemical_analysis_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("biochemical_analyses.biochemical_analysis_id", ondelete="CASCADE"),
        primary_key=True,
    )
    biochemical_indicator_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey(
            "biochemical_indicators.biochemical_indicator_id", ondelete="RESTRICT"
        ),
        primary_key=True,
    )
    measurement_unit_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("measurement_units.measurement_unit_id", ondelete="SET NULL"),
    )
    value: Mapped[Decimal] = mapped_column(Numeric(10, 4))

    analysis: Mapped["BiochemicalAnalysis"] = relationship(
        "BiochemicalAnalysis", lazy="joined"
    )
    indicator: Mapped["BiochemicalIndicator"] = relationship(
        "BiochemicalIndicator", lazy="joined"
    )
    measurement_unit: Mapped["MeasurementUnit | None"] = relationship(
        "MeasurementUnit", lazy="joined"
    )


# ── circular imports ────────────────────────────────────────────────
from src.features.locations.models import Address  # noqa: E402, F811
from src.features.morphology.models import MeasurementUnit  # noqa: E402, F811
from src.features.organizations.models import Organization  # noqa: E402, F811
from src.features.plants.models import Plant  # noqa: E402, F811
