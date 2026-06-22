from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import String
from src.features.taxonomy.models import Genus, Species  # noqa: F401
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class Plant(BaseSqlModel):
    __tablename__ = "plants"

    id: Mapped[PyUUID] = mapped_column(
        "plant_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String)
    species_id: Mapped[PyUUID] = mapped_column(UUID, ForeignKey("species.species_id"))
