from pathlib import Path
from shutil import copyfileobj
from time import time

import numpy as np
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_201_CREATED
from torch import cuda

from models.models import models
from src.mock_data import User, user_db
from src.predictions import get_prediction

models_dir = r"D:\projects\EcoData\backend\models"
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
    return cuda.current_device()


@app.post("/upload_file")
def upload_file(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.post("/models/")
def add_new_model(genus: str, sort_name: str, model_file: UploadFile) -> dict[str, str]:
    model_file_extention = ".pth"
    if Path(model_file.filename).suffix.lower() != model_file_extention:
        return {"message": "The model file must have 'pth' extention"}
    model_name = models_dir + "/" + str(int(time())) + model_file_extention
    models.setdefault(genus, [{"name": sort_name, "path": model_name}])
    print(model_name)
    with open(model_name, "wb") as file:
        copyfileobj(model_file.file, file)
    return {"message": f"The Model is saved with name {model_name}"}


@app.get("/models/")
def get_names_models():
    return models


@app.post("/predictions")
def post_prediction(image: UploadFile):
    img_data = image.file.read()
    img_np = np.fromstring(string=img_data, dtype=np.uint8)
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
        predictions.append({"classifier": type, "probability": get_prediction(img_np)})
    return {
        "predictions": predictions,
        "Access-Control-Allow-Origin": "http://localhost:3000/",
    }
