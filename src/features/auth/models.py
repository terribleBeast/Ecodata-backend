from uuid import uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class SystemRole(BaseSqlModel):
    __tablename__ = "system_roles"

    id: Mapped[PyUUID] = mapped_column(
        "system_role_id", UUID, primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True)
