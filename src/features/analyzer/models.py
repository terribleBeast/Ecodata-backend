from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class NeuralModel(BaseSqlModel):
    __tablename__ = "neural_models"

    id: Mapped[PyUUID] = mapped_column(
        "neural_model_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    species_id: Mapped[PyUUID] = mapped_column(UUID, ForeignKey("species.species_id"))
    name: Mapped[str] = mapped_column(String)
