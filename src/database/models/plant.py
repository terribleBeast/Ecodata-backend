from uuid import UUID as PyUUID
from uuid import uuid4

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models.base import BaseSqlModel


class Plant(BaseSqlModel):
    __tablename__ = "plants"

    id: Mapped[PyUUID] = mapped_column(
        "plant_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    species: Mapped[str] = mapped_column(String)
    genus: Mapped[str] = mapped_column(String)
