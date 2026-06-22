from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Researcher(BaseSqlModel):
    __tablename__ = "researchers"

    id: Mapped[PyUUID] = mapped_column(
        "researcher_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
    )
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    patronymic: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))
    orcid_link: Mapped[str | None] = mapped_column(String(20), unique=True)
    job_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("jobs.job_id", ondelete="SET NULL")
    )
    organization_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("organizations.organization_id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )

    # association — researches this researcher participates in
    researches: Mapped[list["ResearcherResearchAssociation"]] = relationship(
        back_populates="researcher",
        cascade="all, delete-orphan",
    )


# late import to avoid circular dependency
from src.features.research.models import (
    ResearcherResearchAssociation,  # noqa: E402, F401
)
