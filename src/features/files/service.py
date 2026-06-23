import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.files.repository import FileRepo, ImageRepo
from src.shared.database import get_db
from src.shared.rustfs import rustfs
from src.shared.service import BaseService
from src.shared.types import PyUUID

# ── File ───────────────────────────────────────────────────────


async def get_file_repo(session: AsyncSession = Depends(get_db)) -> FileRepo:
    return FileRepo(session)


class FileService(BaseService[FileRepo]):
    def __init__(self, repo: FileRepo):
        self._repo = repo

    async def upload(
        self,
        file: UploadFile,
        bucket: str,
        uploaded_by_user_id: PyUUID | None = None,
    ) -> dict:
        """Upload a file to RustFS and store metadata in the database."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        # Generate deterministic object key: uuid + original extension
        ext = Path(file.filename).suffix or ""
        object_key = str(uuid4()) + ext

        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(file.filename)
        mime_type = mime_type or "application/octet-stream"

        # Read entire file into memory, then upload
        body = await file.read()

        # Upload to RustFS
        result = await rustfs.put_object(
            bucket=bucket,
            key=object_key,
            body=body,
            content_type=mime_type,
        )

        # Store metadata in DB
        file_id = self._repo.new_id()
        await self._repo.create(
            {
                "id": file_id,
                "bucket": bucket,
                "object_key": object_key,   
                "original_filename": file.filename,
                "mime_type": mime_type,
                "size_bytes": result["size_bytes"],
                "checksum": result["checksum"],
                "uploaded_by_user_id": uploaded_by_user_id,
            }
        )

        return {
            "file_id": file_id,
            "bucket": bucket,
            "object_key": object_key,
            "original_filename": file.filename,
            "mime_type": mime_type,
            "size_bytes": result["size_bytes"],
            "checksum": result["checksum"],
        }

    async def download(self, file_id: PyUUID) -> tuple[bytes, str, str]:
        """Download file bytes from RustFS. Returns (bytes, mime_type, filename)."""
        record = await self._repo.get_by_id(file_id)
        if not record:
            raise HTTPException(status_code=404, detail="File not found")
        data = await rustfs.get_object(record.bucket, record.object_key)
        filename = record.original_filename or record.object_key
        mime_type = record.mime_type or "application/octet-stream"
        return data, mime_type, filename

    async def download_stream(self, file_id: PyUUID):
        """Stream file from RustFS. Yields (chunk_generator, mime_type, filename)."""
        record = await self._repo.get_by_id(file_id)
        if not record:
            raise HTTPException(status_code=404, detail="File not found")
        filename = record.original_filename or record.object_key
        mime_type = record.mime_type or "application/octet-stream"
        return (
            rustfs.get_object_stream(record.bucket, record.object_key),
            mime_type,
            filename,
        )

    async def delete(self, id: PyUUID) -> None:
        """Delete file record from DB and object from RustFS."""
        record = await self._repo.get_by_id(id)
        if record:
            await rustfs.delete_object(record.bucket, record.object_key)
        await self._repo.delete(id)


async def get_file_service(
    repo: FileRepo = Depends(get_file_repo),
) -> FileService:
    return FileService(repo)


# ── Image ──────────────────────────────────────────────────────


async def get_image_repo(session: AsyncSession = Depends(get_db)) -> ImageRepo:
    return ImageRepo(session)


class ImageService(BaseService[ImageRepo]):
    def __init__(self, repo: ImageRepo):
        self._repo = repo


async def get_image_service(
    repo: ImageRepo = Depends(get_image_repo),
) -> ImageService:
    return ImageService(repo)
