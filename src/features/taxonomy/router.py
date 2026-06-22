from typing import Annotated

from fastapi import APIRouter, Depends, status
from src.features.taxonomy.schemas import (
    GenusCreate,
    GenusRead,
    GenusUpdate,
    SpeciesCreate,
    SpeciesRead,
    SpeciesUpdate,
)
from src.features.taxonomy.service import (
    GenusService,
    SpeciesService,
    get_genus_service,
    get_species_service,
)
from src.shared.types import PyUUID

genera_router = APIRouter(prefix="/plants/genera", tags=["genera"])


# ── Genera ──────────────────────────────────────────────────────────────


@genera_router.get("/", response_model=list[GenusRead])
async def genus_list(
    service: Annotated[GenusService, Depends(get_genus_service)],
    q: str | None = None,
):
    if q:
        return await service.search_by_field("name", q)
    return await service.get_all()


@genera_router.get("/{id}", response_model=GenusRead)
async def genus_get(
    id: PyUUID,
    service: Annotated[GenusService, Depends(get_genus_service)],
):
    item = await service.get_one(id)
    return item


@genera_router.post("/", response_model=GenusRead, status_code=status.HTTP_201_CREATED)
async def genus_create(
    service: Annotated[GenusService, Depends(get_genus_service)],
    body: GenusCreate,
):
    item = await service.get_one(await service.create(body))
    return item


@genera_router.put("/{id}", response_model=GenusRead)
async def genus_update(
    id: PyUUID,
    body: GenusUpdate,
    service: Annotated[GenusService, Depends(get_genus_service)],
):
    await service.update(id, body)
    item = await service.get_one(id)
    return item


@genera_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def genus_delete(
    id: PyUUID,
    service: Annotated[GenusService, Depends(get_genus_service)],
):
    await service.delete(id)


species_router = APIRouter(prefix="/species", tags=["species"])
# ── Species ─────────────────────────────────────────────────────────────


@species_router.get("/", response_model=list[SpeciesRead])
async def species_list(
    service: Annotated[SpeciesService, Depends(get_species_service)],
    genus_id: PyUUID | None = None,
    q: str | None = None,
):
    if genus_id:
        return await service.search_by_field("genus_id", genus_id)
    if q:
        return await service.search_by_field("name", q)
    return await service.get_all()


@species_router.get("/{id}", response_model=SpeciesRead)
async def species_get(
    id: PyUUID,
    service: Annotated[SpeciesService, Depends(get_species_service)],
):
    item = await service.get_one(id)
    return item


@species_router.post(
    "/", response_model=SpeciesRead, status_code=status.HTTP_201_CREATED
)
async def species_create(
    service: Annotated[SpeciesService, Depends(get_species_service)],
    body: SpeciesCreate,
):
    item = await service.get_one(await service.create(body))
    return item


@species_router.put("/{id}", response_model=SpeciesRead)
async def species_update(
    id: PyUUID,
    body: SpeciesUpdate,
    service: Annotated[SpeciesService, Depends(get_species_service)],
):
    await service.update(id, body)
    item = await service.get_one(id)
    return item


@species_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def species_delete(
    id: PyUUID,
    service: Annotated[SpeciesService, Depends(get_species_service)],
):
    await service.delete(id)
