from typing import Annotated

from fastapi import APIRouter, Depends, Query
from src.features.research.schemas import (
    ResearchAssignResearchers,
    ResearchCreate,
    ResearchResponse,
    ResearchUpdate,
)
from src.features.research.service import ResearchService, get_research_service
from src.shared.types import PyUUID

router = APIRouter(prefix="/researches", tags=["researches"])


@router.get("/", response_model=list[ResearchResponse])
async def research_list(
    service: Annotated[ResearchService, Depends(get_research_service)],
    status: Annotated[str | None, Query()] = None,
):
    if status:
        return await service.search_by_status(status)
    return await service.get_all()


@router.get("/{id}", response_model=ResearchResponse)
async def research_get(
    id: PyUUID,
    service: Annotated[ResearchService, Depends(get_research_service)],
):
    return await service.get_one(id)


@router.post("/", response_model=PyUUID, status_code=201)
async def research_create(
    service: Annotated[ResearchService, Depends(get_research_service)],
    research: ResearchCreate,
):
    return await service.create(research)


@router.patch("/{id}", response_model=PyUUID)
async def research_update(
    id: PyUUID,
    research: ResearchUpdate,
    service: Annotated[ResearchService, Depends(get_research_service)],
):
    return await service.update(id, research)


@router.delete("/{id}", status_code=204)
async def research_delete(
    id: PyUUID,
    service: Annotated[ResearchService, Depends(get_research_service)],
):
    await service.delete(id)


@router.post("/invite/{research_id}", status_code=204)
async def research_add_researchers(
    research_id: PyUUID,
    body: ResearchAssignResearchers,
    service: Annotated[ResearchService, Depends(get_research_service)],
):
    await service.add_researchers(research_id, body.researcher_ids)


@router.delete("/seprate/{research_id}", status_code=204)
async def research_remove_researchers(
    research_id: PyUUID,
    body: ResearchAssignResearchers,
    service: Annotated[ResearchService, Depends(get_research_service)],
):
    await service.remove_researchers(research_id, body.researcher_ids)
