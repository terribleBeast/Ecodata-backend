from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID

if TYPE_CHECKING:
    from src.features.auth.models import SystemRole
    from src.features.jobs.models import Job
    from src.features.organizations.models import Organization
    from src.features.research.models import ResearcherResearchAssociation


class Researcher(BaseSqlModel):
    __tablename__ = "researchers"

    id: Mapped[PyUUID] = mapped_column(
        "researcher_id", UUID, primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    system_role_id: Mapped[PyUUID] = mapped_column(
        UUID,
        ForeignKey("system_roles.system_role_id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))
    orcid_link: Mapped[str | None] = mapped_column(String(20), unique=True)
    job_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey("jobs.job_id", ondelete="SET NULL", onupdate="CASCADE"),
    )
    organization_id: Mapped[PyUUID | None] = mapped_column(
        UUID,
        ForeignKey(
            "organizations.organization_id", ondelete="SET NULL", onupdate="CASCADE"
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        nullable=False,
    )

    researches: Mapped[list["ResearcherResearchAssociation"]] = relationship(
        back_populates="researcher",
        cascade="all, delete-orphan",
    )

    # eager-loaded for readable API responses
    system_role: Mapped["SystemRole"] = relationship(lazy="joined")
    job: Mapped["Job | None"] = relationship(lazy="joined")
    organization: Mapped["Organization | None"] = relationship(lazy="joined")


from src.features.research.models import (
    ResearcherResearchAssociation,  # noqa: E402, F401
)
