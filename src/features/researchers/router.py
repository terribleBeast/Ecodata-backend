from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from src.features.researchers.schemas import (
    ResearcherCreate,
    ResearcherResponse,
    ResearcherUpdate,
)
from src.features.researchers.service import ResearcherService, get_researcher_service
from src.shared.types import PyUUID

router = APIRouter(prefix="/researchers", tags=["researchers"])


@router.get("/", response_model=list[ResearcherResponse])
async def researcher_list(
    service: Annotated[ResearcherService, Depends(get_researcher_service)],
    ids: list[PyUUID] | None = Query(None),
):
    if ids:
        return await service.get_by_ids(ids)

    return await service.get_all()


@router.get("/{id}", response_model=ResearcherResponse)
async def researcher_get(
    id: PyUUID,
    service: Annotated[ResearcherService, Depends(get_researcher_service)],
):
    user = await service.get_one(id)
    if not user:
        raise HTTPException(
            status_code=404,
        )
    return user


@router.post("/", response_model=PyUUID, status_code=201)
async def researcher_create(
    service: Annotated[ResearcherService, Depends(get_researcher_service)],
    researcher: ResearcherCreate,
):
    return await service.create(researcher)


@router.patch("/{id}", response_model=PyUUID)
async def researcher_update(
    id: PyUUID,
    researcher: ResearcherUpdate,
    service: Annotated[ResearcherService, Depends(get_researcher_service)],
):
    return await service.update(id, researcher)


@router.delete("/{id}", status_code=204)
async def researcher_delete(
    id: PyUUID,
    service: Annotated[ResearcherService, Depends(get_researcher_service)],
):
    await service.delete(id)
