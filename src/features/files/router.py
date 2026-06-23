from typing import Annotated

from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.responses import StreamingResponse
from src.features.files.schemas import (
    FileCreate,
    FileResponse,
    FileUpdate,
    FileUploadResponse,
    ImageCreate,
    ImageResponse,
    ImageUpdate,
)
from src.features.files.service import (
    FileService,
    ImageService,
    get_file_service,
    get_image_service,
)
from src.shared.types import PyUUID

files_router = APIRouter(prefix="/files", tags=["files"])

# ── Metadata CRUD ─────────────────────────────────────────────


@files_router.get("/", response_model=list[FileResponse])
async def file_list(
    service: Annotated[FileService, Depends(get_file_service)],
):
    return await service.get_all()


@files_router.get("/{id}", response_model=FileResponse)
async def file_get(
    id: PyUUID,
    service: Annotated[FileService, Depends(get_file_service)],
):
    return await service.get_one(id)


@files_router.post("/", response_model=PyUUID, status_code=201)
async def file_create(
    service: Annotated[FileService, Depends(get_file_service)],
    item: FileCreate,
):
    """Create a metadata-only file record (no upload to RustFS)."""
    return await service.create(item)


@files_router.patch("/{id}", response_model=PyUUID)
async def file_update(
    id: PyUUID,
    item: FileUpdate,
    service: Annotated[FileService, Depends(get_file_service)],
):
    return await service.update(id, item)


@files_router.delete("/{id}", status_code=204)
async def file_delete(
    id: PyUUID,
    service: Annotated[FileService, Depends(get_file_service)],
):
    await service.delete(id)


# ── Upload / Download ─────────────────────────────────────────


@files_router.post("/upload", response_model=FileUploadResponse, status_code=201)
async def file_upload(
    file: UploadFile,
    bucket: Annotated[str, Query(description="RustFS bucket name")],
    service: Annotated[FileService, Depends(get_file_service)],
):
    """Upload a file to RustFS and store its metadata."""
    return await service.upload(file=file, bucket=bucket)


@files_router.get("/{id}/download")
async def file_download(
    id: PyUUID,
    service: Annotated[FileService, Depends(get_file_service)],
):
    """Download a file from RustFS."""
    data, mime_type, filename = await service.download(id)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        iter([data]),
        media_type=mime_type,
        headers=headers,
    )


# ── Images ─────────────────────────────────────────────────────

images_router = APIRouter(prefix="/images", tags=["images"])


@images_router.get("/", response_model=list[ImageResponse])
async def image_list(
    service: Annotated[ImageService, Depends(get_image_service)],
):
    return await service.get_all()


@images_router.get("/{id}", response_model=ImageResponse)
async def image_get(
    id: PyUUID,
    service: Annotated[ImageService, Depends(get_image_service)],
):
    return await service.get_one(id)


@images_router.post("/", response_model=PyUUID, status_code=201)
async def image_create(
    service: Annotated[ImageService, Depends(get_image_service)],
    item: ImageCreate,
):
    return await service.create(item)


@images_router.patch("/{id}", response_model=PyUUID)
async def image_update(
    id: PyUUID,
    item: ImageUpdate,
    service: Annotated[ImageService, Depends(get_image_service)],
):
    return await service.update(id, item)


@images_router.delete("/{id}", status_code=204)
async def image_delete(
    id: PyUUID,
    service: Annotated[ImageService, Depends(get_image_service)],
):
    await service.delete(id)
