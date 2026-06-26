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
from src.features.auth.router import roles_router
from src.features.auth.router import router as auth_router
from src.features.biochemistry.router import (
    analyses_router,
    indicators_router,
    laboratories_router,
    values_router,
)
from src.features.files.router import files_router, images_router
from src.features.jobs.router import router as jobs_router
from src.features.leaves.router import leaf_artifacts_router, leaves_router
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
from src.features.morphology.router import (
    leaf_morph_values_router,
    measurement_units_router,
    morphological_features_router,
)
from src.features.organizations.router import org_type_router
from src.features.organizations.router import router as organizations_router
from src.features.plants.router import (
    leaf_blade_types_router,
    location_on_plant_router,
    plant_descriptions_router,
    plant_life_forms_router,
    plants_router,
    side_of_the_world_router,
)
from src.features.research.router import router as research_router
from src.features.researchers.router import router as researchers_router
from src.features.taxonomy.router import genera_router, species_router
from src.shared import rustfs
from src.shared.auth_dependencies import require_auth, require_auth_for_writes
from src.shared.auth_middleware import AuthMiddleware
from src.shared.database import PostgresSession, get_db
from src.shared.rustfs import rustfs
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


app = FastAPI(lifespan=lifespan, title="EcoData")

app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_bearer = HTTPBearer(auto_error=False)
api_router = APIRouter(prefix="/api/v1")

# ── Public (no auth scheme declared) ──────────────────────────

api_router.include_router(auth_router)
api_router.include_router(roles_router)

api_router.include_router(species_router)
api_router.include_router(genera_router)
api_router.include_router(logs_router)

# ── Reads public, writes require auth ─────────────────────────

_read_public = [Depends(require_auth_for_writes), Depends(_bearer)]

api_router.include_router(plants_router, dependencies=_read_public)
api_router.include_router(plant_life_forms_router, dependencies=_read_public)
api_router.include_router(leaf_blade_types_router, dependencies=_read_public)
api_router.include_router(plant_descriptions_router, dependencies=_read_public)
api_router.include_router(side_of_the_world_router, dependencies=_read_public)
api_router.include_router(location_on_plant_router, dependencies=_read_public)
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
api_router.include_router(files_router, dependencies=_read_public)
api_router.include_router(images_router, dependencies=_read_public)
api_router.include_router(leaves_router, dependencies=_read_public)
api_router.include_router(leaf_artifacts_router, dependencies=_read_public)
api_router.include_router(measurement_units_router, dependencies=_read_public)
api_router.include_router(morphological_features_router, dependencies=_read_public)
api_router.include_router(leaf_morph_values_router, dependencies=_read_public)
api_router.include_router(laboratories_router, dependencies=_read_public)
api_router.include_router(indicators_router, dependencies=_read_public)
api_router.include_router(analyses_router, dependencies=_read_public)
api_router.include_router(values_router, dependencies=_read_public)

# ── Analyzer requires auth on all endpoints ───────────────────

_analyzer_deps = [Depends(require_auth), Depends(_bearer)]
api_router.include_router(analyzer_router, dependencies=_analyzer_deps)
api_router.include_router(analyzer_ws_router)

app.include_router(api_router)


@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": str(exc)})


@app.get("/db")
async def root(db: AsyncSession = Depends(get_db)):
    return {"message": "Database connected!"}


@app.get("/rustfs/health")
async def rustfs_health():
    result = await rustfs.healthcheck()

    if result["status"] == "error":
        raise HTTPException(status_code=503, detail=result["message"])

    return result


@app.get("/rustfs/config")
async def rustfs_config():
    return {
        "endpoint": rustfs._endpoint_url,
        "access_key": rustfs._access_key,
    }


import httpx


@app.get("/rustfs/http-test")
async def rustfs_http_test():
    try:
        async with httpx.AsyncClient(
            timeout=5,
            trust_env=False,  # important: ignore system proxy env vars
            http1=True,
            http2=False,
            headers={
                "Connection": "close",
                "Accept": "application/xml",
            },
        ) as client:
            response = await client.get("http://127.0.0.1:19010/new-data")

        return {
            "status": "ok",
            "http_status": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
        }

    except Exception as exc:
        return {
            "status": "error",
            "exception": type(exc).__name__,
            "repr": repr(exc),
            "message": str(exc),
        }
