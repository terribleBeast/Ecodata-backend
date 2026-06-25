import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.shared.models import BaseSqlModel
from src.shared.types import PyUUID


class ImageTypeEnum(str, enum.Enum):
    original = "original"
    cropped = "cropped"
    processed = "processed"
    visualisation = "visualisation"


class File(BaseSqlModel):
    __tablename__ = "files"

    id: Mapped[PyUUID] = mapped_column("file_id", UUID, primary_key=True, default=uuid4)
    bucket: Mapped[str] = mapped_column(String(100))
    object_key: Mapped[str] = mapped_column(Text)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(100))
    size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    checksum: Mapped[str | None] = mapped_column(String(128))
    uploaded_by_researcher_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("researchers.researcher_id", ondelete="SET NULL")
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )

    uploaded_by: Mapped["Researcher | None"] = relationship(
        lazy="joined", foreign_keys=[uploaded_by_researcher_id]
    )

    __table_args__ = (
        UniqueConstraint("bucket", "object_key", name="uq_files_bucket_object_key"),
    )


class Image(BaseSqlModel):
    __tablename__ = "images"

    id: Mapped[PyUUID] = mapped_column(
        "image_id", UUID, primary_key=True, default=uuid4
    )
    file_id: Mapped[PyUUID] = mapped_column(
        UUID, ForeignKey("files.file_id", ondelete="RESTRICT"), unique=True
    )
    width_px: Mapped[int | None] = mapped_column(Integer)
    height_px: Mapped[int | None] = mapped_column(Integer)
    image_type: Mapped[ImageTypeEnum] = mapped_column(
        Enum(ImageTypeEnum, name="image_type", create_type=False),
        default=ImageTypeEnum.original,
        server_default="original",
    )
    uploaded_by_researcher_id: Mapped[PyUUID | None] = mapped_column(
        UUID, ForeignKey("researchers.researcher_id", ondelete="SET NULL")
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=func.now()
    )

    file: Mapped["File"] = relationship(lazy="joined")
    uploaded_by: Mapped["Researcher | None"] = relationship(
        lazy="joined", foreign_keys=[uploaded_by_researcher_id]
    )


from src.features.researchers.models import Researcher  # noqa: E402, F401
