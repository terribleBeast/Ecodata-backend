from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Research(BaseSqlModel):
    __tablename__ = "researches"

    id: Mapped[PyUUID] = mapped_column(
        "research_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String(255))
    goal: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        Enum(
            "draft",
            "active",
            "completed",
            "archived",
            name="research_status",
            create_type=False,
        ),
        default="draft",
    )
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    created_by_researcher_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("researchers.researcher_id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),
    )

    # association — researchers participating in this research
    researchers: Mapped[list["ResearcherResearchAssociation"]] = relationship(
        back_populates="research",
        cascade="all, delete-orphan",
    )


class ResearcherResearchAssociation(BaseSqlModel):
    __tablename__ = "researcher_research_association"

    researcher_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("researchers.researcher_id", ondelete="CASCADE"),
        primary_key=True,
    )
    research_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("researches.research_id", ondelete="CASCADE"),
        primary_key=True,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )

    researcher: Mapped["Researcher"] = relationship(back_populates="researches")
    research: Mapped["Research"] = relationship(back_populates="researchers")


# late import to avoid circular dependency
from src.features.researchers.models import Researcher  # noqa: E402, F401
