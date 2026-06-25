from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID

# ── File ───────────────────────────────────────────────────────


class FileCreate(BaseModel):
    bucket: Annotated[str, Field(min_length=1, max_length=100)]
    object_key: Annotated[str, Field(min_length=1)]
    original_filename: Annotated[str | None, Field(max_length=255)] = None
    mime_type: Annotated[str | None, Field(max_length=100)] = None
    size_bytes: int | None = None
    checksum: Annotated[str | None, Field(max_length=128)] = None
    uploaded_by_researcher_id: PyUUID | None = None


class FileUpdate(BaseModel):
    bucket: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    object_key: Annotated[str | None, Field(min_length=1)] = None
    original_filename: Annotated[str | None, Field(max_length=255)] = None
    mime_type: Annotated[str | None, Field(max_length=100)] = None
    size_bytes: int | None = None
    checksum: Annotated[str | None, Field(max_length=128)] = None
    uploaded_by_researcher_id: PyUUID | None = None


class FileResponse(BaseSchema):
    file_id: PyUUID = Field(validation_alias="id")
    bucket: str
    object_key: str
    original_filename: str | None
    mime_type: str | None
    size_bytes: int | None
    checksum: str | None
    uploaded_by_researcher_id: PyUUID | None
    uploaded_at: datetime


class FileUploadResponse(BaseModel):
    file_id: PyUUID
    bucket: str
    object_key: str
    original_filename: str | None
    mime_type: str | None
    size_bytes: int
    checksum: str


class FileNested(BaseModel):
    file_id: PyUUID = Field(validation_alias="id")
    original_filename: str | None


# ── Image ──────────────────────────────────────────────────────


class ImageCreate(BaseModel):
    file_id: PyUUID
    width_px: int | None = None
    height_px: int | None = None
    image_type: str = "original"
    uploaded_by_researcher_id: PyUUID | None = None


class ImageUpdate(BaseModel):
    width_px: int | None = None
    height_px: int | None = None
    image_type: str | None = None
    uploaded_by_researcher_id: PyUUID | None = None


class ImageResponse(BaseSchema):
    image_id: PyUUID = Field(validation_alias="id")
    file: FileNested
    width_px: int | None
    height_px: int | None
    image_type: str
    uploaded_by_researcher_id: PyUUID | None
    uploaded_at: datetime
