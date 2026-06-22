import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.analyzer.engine import inference_executor, model_cache
from src.features.analyzer.router import router as analyzer_router
from src.features.analyzer.ws_router import router as analyzer_ws_router
from src.features.auth.router import router as auth_router
from src.features.logs.router import router as logs_router
from src.features.plants.router import router as plant_router
from src.features.research.router import router as research_router
from src.features.taxonomy.router import genera_router, species_router
from src.shared.database import PostgresSession, get_db
from src.utils.logger import log_config
from starlette.responses import JSONResponse

logger = logging.getLogger("app")
dictConfig(log_config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    database_url = "postgresql+asyncpg://koval@localhost:5432/ecodata"
    await PostgresSession.init(database_url)

    yield

    # Shutdown
    await PostgresSession.close()
    model_cache.clear()  # освободить VRAM
    inference_executor.shutdown(wait=True)


app = FastAPI(lifespan=lifespan)
api_router = APIRouter(
    prefix="/api/v1",
)
# Register feature routers under the API v1 prefix
api_router.include_router(auth_router)
api_router.include_router(plant_router)
api_router.include_router(analyzer_router)
api_router.include_router(analyzer_ws_router)
api_router.include_router(research_router)
api_router.include_router(logs_router)
api_router.include_router(species_router)
api_router.include_router(genera_router)

# origins = [
#     "http://localhost",
#     "http://localhost:5173",
# ]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    # allow_credentials=True,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"message": "I'm an exception"}
    )


@app.get("/db")
async def root(db: AsyncSession = Depends(get_db)):
    return {"message": "Database connected!"}
