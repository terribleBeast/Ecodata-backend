from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
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
