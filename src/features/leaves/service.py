from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.leaves.repository import LeafArtifactRepo, LeafRepo
from src.features.leaves.schemas import LeafPlantAssignmentBatch
from src.shared.database import get_db
from src.shared.service import BaseService


async def get_leaf_repo(session: AsyncSession = Depends(get_db)) -> LeafRepo:
    return LeafRepo(session)


class LeafService(BaseService):
    def __init__(self, repo: LeafRepo):
        self._repo = repo

    async def assign_plants(self, body: LeafPlantAssignmentBatch) -> None:
        assignments = [item.model_dump() for item in body.assignments]

        try:
            await self._repo.assign_plants_to_leaves(assignments)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


async def get_leaf_service(
    repo: LeafRepo = Depends(get_leaf_repo),
) -> LeafService:
    return LeafService(repo)


async def get_leaf_artifact_repo(
    session: AsyncSession = Depends(get_db),
) -> LeafArtifactRepo:
    return LeafArtifactRepo(session)


class LeafArtifactService(BaseService):
    def __init__(self, repo: LeafArtifactRepo):
        self._repo = repo


async def get_leaf_artifact_service(
    repo: LeafArtifactRepo = Depends(get_leaf_artifact_repo),
) -> LeafArtifactService:
    return LeafArtifactService(repo)
