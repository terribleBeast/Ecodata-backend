import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.analyzer.engine import inference_executor, model_cache
from src.features.analyzer.router import router as analyzer_router
from src.features.analyzer.ws_router import router as analyzer_ws_router
from src.features.auth.router import roles_router, users_router
from src.features.auth.router import router as auth_router
from src.features.jobs.router import router as jobs_router
from src.features.locations.router import (
    addresses_router,
    countries_router,
    districts_router,
    house_numbers_router,
    locations_router,
    regions_router,
    settlement_types_router,
    settlements_router,
    streets_router,
)
from src.features.logs.router import router as logs_router
from src.features.organizations.router import org_type_router
from src.features.organizations.router import router as organizations_router
from src.features.plants.router import router as plant_router
from src.features.research.router import router as research_router
from src.features.researchers.router import router as researchers_router
from src.features.taxonomy.router import genera_router, species_router
from src.shared.auth_dependencies import require_auth, require_auth_for_writes
from src.shared.auth_middleware import AuthMiddleware
from src.shared.database import PostgresSession, get_db
from src.utils.logger import log_config
from starlette.responses import JSONResponse

logger = logging.getLogger("app")
dictConfig(log_config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = "postgresql+asyncpg://koval@localhost:5432/ecodata"
    await PostgresSession.init(database_url)

    yield

    await PostgresSession.close()
    model_cache.clear()
    inference_executor.shutdown(wait=True)


app = FastAPI(lifespan=lifespan)

# ── Middleware (order matters: last added = outermost) ────────

app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API v1 ────────────────────────────────────────────────────

_bearer = HTTPBearer(auto_error=False)

api_router = APIRouter(prefix="/api/v1")

# Public — no bearer scheme declared (login/register don't need a token)
api_router.include_router(auth_router)
api_router.include_router(roles_router)
api_router.include_router(users_router)

# Reads public, writes require auth.
# HTTPBearer(auto_error=False) declares the scheme to OpenAPI natively
# so Swagger shows the Authorize button on these endpoints without
# actually enforcing anything (enforcement is done by require_auth_for_writes).
_read_public = [Depends(require_auth_for_writes), Depends(_bearer)]

api_router.include_router(plant_router, dependencies=_read_public)
api_router.include_router(research_router, dependencies=_read_public)
api_router.include_router(researchers_router, dependencies=_read_public)
api_router.include_router(jobs_router, dependencies=_read_public)
api_router.include_router(organizations_router, dependencies=_read_public)
api_router.include_router(org_type_router, dependencies=_read_public)
api_router.include_router(countries_router, dependencies=_read_public)
api_router.include_router(regions_router, dependencies=_read_public)
api_router.include_router(districts_router, dependencies=_read_public)
api_router.include_router(settlement_types_router, dependencies=_read_public)
api_router.include_router(settlements_router, dependencies=_read_public)
api_router.include_router(streets_router, dependencies=_read_public)
api_router.include_router(house_numbers_router, dependencies=_read_public)
api_router.include_router(addresses_router, dependencies=_read_public)
api_router.include_router(locations_router, dependencies=_read_public)

# All analyzer endpoints require auth
_analyzer_deps = [Depends(require_auth), Depends(_bearer)]
api_router.include_router(analyzer_router, dependencies=_analyzer_deps)
api_router.include_router(analyzer_ws_router)

# Taxonomy — read-only, public (no auth scheme declared)
api_router.include_router(species_router)
api_router.include_router(genera_router)

# Internal
api_router.include_router(logs_router)

app.include_router(api_router)


@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": str(exc)})


@app.get("/db")
async def root(db: AsyncSession = Depends(get_db)):
    return {"message": "Database connected!"}
