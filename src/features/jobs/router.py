from typing import Annotated

from fastapi import APIRouter, Depends
from src.features.jobs.schemas import JobCreate, JobResponse, JobUpdate
from src.features.jobs.service import JobService, get_job_service
from src.shared.types import PyUUID

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobResponse])
async def job_list(
    service: Annotated[JobService, Depends(get_job_service)],
):
    return await service.get_all()


@router.get("/{id}", response_model=JobResponse)
async def job_get(
    id: PyUUID,
    service: Annotated[JobService, Depends(get_job_service)],
):
    return await service.get_one(id)


@router.post("/", response_model=PyUUID, status_code=201)
async def job_create(
    service: Annotated[JobService, Depends(get_job_service)],
    job: JobCreate,
):
    return await service.create(job)


@router.patch("/{id}", response_model=PyUUID)
async def job_update(
    id: PyUUID,
    job: JobUpdate,
    service: Annotated[JobService, Depends(get_job_service)],
):
    return await service.update(id, job)


@router.delete("/{id}", status_code=204)
async def job_delete(
    id: PyUUID,
    service: Annotated[JobService, Depends(get_job_service)],
):
    await service.delete(id)
