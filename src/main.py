from random import random

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.mock_data import User, user_db

app = FastAPI()
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


@app.get("/")
def hello():
    return "Hello, world!"


@app.post("/upload_file")
def upload_file(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/predictions")
def get_prediction():
    return "hello"


@app.post("/predictions")
def post_prediction():

    types = [
        "Феникс Уральское",
        "Уральское наливное",
        "Сувенир Алтая",
        "Подарок садоводам",
        "Заветное",
        "Жебровское",
        "Жар-птица",
        "Алтайское румяное",
        "Алтайское зимнее",
        "Алтайская красавица",
    ]
    predictions: list[dict[str, str | float]] = []
    for type in types:
        predictions.append({"classifier": type, "probability": random() * 100})
    return {
        "predictions": predictions,
        "Access-Control-Allow-Origin": "http://localhost:3000/",
    }
 