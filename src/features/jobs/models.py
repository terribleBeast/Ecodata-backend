from uuid import uuid4

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Job(BaseSqlModel):
    __tablename__ = "jobs"

    id: Mapped[PyUUID] = mapped_column(
        "job_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
