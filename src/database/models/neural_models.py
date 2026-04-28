from uuid import UUID as PyUUID
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import BaseSqlModel


class NeuralModel(BaseSqlModel):
    __tablename__ = "neural_models"
    # __table_args__ = (
    #     ForeignKeyConstraint(
    #         ["plant_id"], ["neural_model_plant_associations.plant_id"]
    #     ),
    # )
    id: Mapped[PyUUID] = mapped_column(
        "neural_model_id",
        UUID,
        primary_key=True,
        default=uuid4,
    )
    plant_id: Mapped[PyUUID] = mapped_column(UUID, ForeignKey("Plant.id"))
    model_name: Mapped[str] = mapped_column(String)
