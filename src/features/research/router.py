from typing import Annotated

from fastapi import APIRouter, Depends
from src.features.research.schemas import ResearchCreate
from src.features.research.service import ResearchService, get_research_service
from src.shared.types import PyUUID

router = APIRouter(prefix="/researches", tags=["researches"])


@router.get("/")
async def research_list(
    service: Annotated[ResearchService, Depends(get_research_service)],
):
    items = await service.get_all()
    return items


@router.post("/")
async def research_create(
    service: Annotated[ResearchService, Depends(get_research_service)],
    research: ResearchCreate,
):
    result = await service.create(research)
    return result


@router.delete("/{id}")
async def research_delete(
    id: PyUUID,
    service: Annotated[ResearchService, Depends(get_research_service)],
):
    await service.delete(id)
