from typing import Annotated

from fastapi import APIRouter, Depends
from src.features.leaves.schemas import (
    LeafArtifactCreate,
    LeafArtifactResponse,
    LeafArtifactUpdate,
    LeafCreate,
    LeafResponse,
    LeafUpdate,
)
from src.features.leaves.service import (
    LeafArtifactService,
    LeafService,
    get_leaf_artifact_service,
    get_leaf_service,
)
from src.shared.types import PyUUID

leaves_router = APIRouter(prefix="/leaves", tags=["leaves"])
leaf_artifacts_router = APIRouter(prefix="/leaf-artifacts", tags=["leaf-artifacts"])


# ── Leaves CRUD ────────────────────────────────────────────────


@leaves_router.get("/", response_model=list[LeafResponse])
async def leaf_list(
    service: Annotated[LeafService, Depends(get_leaf_service)],
):
    items = await service.get_all()
    return items


@leaves_router.get("/{id}", response_model=LeafResponse)
async def leaf_get(
    id: PyUUID,
    service: Annotated[LeafService, Depends(get_leaf_service)],
):
    return await service.get_one(id)


@leaves_router.post("/", response_model=PyUUID)
async def leaf_create(
    service: Annotated[LeafService, Depends(get_leaf_service)],
    leaf: LeafCreate,
):
    result = await service.create(leaf)
    return result


@leaves_router.put("/{id}", response_model=PyUUID)
async def leaf_update(
    id: PyUUID,
    leaf: LeafUpdate,
    service: Annotated[LeafService, Depends(get_leaf_service)],
):
    return await service.update(id, leaf)


@leaves_router.delete("/{id}")
async def leaf_delete(
    id: PyUUID,
    service: Annotated[LeafService, Depends(get_leaf_service)],
):
    await service.delete(id)


# ── Leaf Artifacts CRUD ────────────────────────────────────────


@leaf_artifacts_router.get("/", response_model=list[LeafArtifactResponse])
async def leaf_artifact_list(
    service: Annotated[LeafArtifactService, Depends(get_leaf_artifact_service)],
):
    items = await service.get_all()
    return items


@leaf_artifacts_router.get("/{id}", response_model=LeafArtifactResponse)
async def leaf_artifact_get(
    id: PyUUID,
    service: Annotated[LeafArtifactService, Depends(get_leaf_artifact_service)],
):
    return await service.get_one(id)


@leaf_artifacts_router.post("/", response_model=PyUUID)
async def leaf_artifact_create(
    service: Annotated[LeafArtifactService, Depends(get_leaf_artifact_service)],
    artifact: LeafArtifactCreate,
):
    result = await service.create(artifact)
    return result


@leaf_artifacts_router.put("/{id}", response_model=PyUUID)
async def leaf_artifact_update(
    id: PyUUID,
    artifact: LeafArtifactUpdate,
    service: Annotated[LeafArtifactService, Depends(get_leaf_artifact_service)],
):
    return await service.update(id, artifact)


@leaf_artifacts_router.delete("/{id}")
async def leaf_artifact_delete(
    id: PyUUID,
    service: Annotated[LeafArtifactService, Depends(get_leaf_artifact_service)],
):
    await service.delete(id)
