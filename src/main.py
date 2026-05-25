import csv
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.api import router
from src.database.session import PostgresSession
from src.utils.logger import log_config

dictConfig(log_config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    database_url = "postgresql+asyncpg://postgres:@localhost:5432/ecodata"
    await PostgresSession.init(database_url)

    yield

    # Shutdown
    await PostgresSession.close()


models_dir = r"D:\projects\EcoData\backend\src\models"
app = FastAPI(lifespan=lifespan)
api = APIRouter(prefix="/api/v1")

api.include_router(router)
app.include_router(api)
origins = [
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/research/{research_id}/predictions")
def post_prediction(research_id: int):
    with open(r"D:\Downloads\result (8).csv", "r", encoding="utf-8") as file:
        data = csv.reader(file)

        return JSONResponse([*data])


@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"message": "I'm an exception"}
    )


# @app.get("/exc")
# async def exception():
#     raise HTTPException(status_code=400)


@app.post("/api/v1/user/login/")
async def loginUser():

    user = {"id": 1, "name": "Alex", "surname": "Doe", "patronymic": "Don"}

    return JSONResponse({"data": user, "token": "1234"})
