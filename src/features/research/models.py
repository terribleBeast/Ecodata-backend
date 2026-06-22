from uuid import uuid4

from sqlalchemy import ARRAY, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Research(BaseSqlModel):
    __tablename__ = "researches"

    id: Mapped[PyUUID] = mapped_column(
        "plant_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    title: Mapped[str] = mapped_column(String)
    goal: Mapped[str] = mapped_column(String)
    researchers_id: Mapped[list[PyUUID]] = mapped_column(ARRAY(UUID))
