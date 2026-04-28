# src/database/dependencies.py
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repository import PlantRepo
from src.database.session import PostgresSession


async def get_db(request: Request) -> AsyncSession:
    """Dependency to get database session"""
    session = await PostgresSession.get_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# For repositories
async def get_plant_repo(session: AsyncSession = Depends(get_db)) -> PlantRepo:
    return PlantRepo(session)
