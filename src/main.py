import csv
from contextlib import asynccontextmanager

import numpy as np
from fastapi import APIRouter, FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.api import router
from src.database.session import PostgresSession

# from src.predictions import get_prediction


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
    "http://localhost:3000",
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
