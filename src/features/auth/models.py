from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
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


class User(BaseSqlModel):
    __tablename__ = "users"

    id: Mapped[PyUUID] = mapped_column("user_id", UUID, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    system_role_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("system_roles.system_role_id", ondelete="RESTRICT")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),
    )
