import json
from pathlib import Path
from shutil import copyfileobj
from time import time
from typing import Annotated, Any

import numpy as np
import torch
from fastapi import APIRouter, Depends, UploadFile
from pydantic.main import BaseModel
from starlette.responses import JSONResponse
from torchvision.io import ImageReadMode, decode_image

from src.api.deps import neural_model_service, plant_service
from src.database.models.neural_models import PyUUID
from src.services.base import BaseService
from src.services.predictions import get_prediction, load_model
from src.shemas.neural_model import NeuralModelCreate

router = APIRouter(prefix="/neural-models", tags=["neural-models"])


@router.get("/")
async def neural_model_list(
    service: Annotated[BaseService, Depends(neural_model_service)],
):
    items = await service.get_all()
    return items


@router.post("/")
async def create_neural_model(
    service: Annotated[BaseService, Depends(neural_model_service)],
    # model: NeuralModelCreate,
    plant_id: PyUUID,
    model_file: UploadFile,
):
    models_dir = r"D:\projects\Ecodata\backend\src\models"
    model_file_extension = ".pth"

    if Path(model_file.filename).suffix.lower() != model_file_extension:
        return {"message": "The model file must have 'pth' extension"}
    model_name = str(int(time())) + model_file_extension
    path = models_dir + "/" + model_name
    await service.create(NeuralModelCreate(plant_id=plant_id, model_name=model_name))
    with open(path, "wb") as file:
        copyfileobj(model_file.file, file)
    return {"message": f"The Model is saved with name {path}"}


@router.delete("/{id}")
async def delete_neural_model(
    id: PyUUID, service: Annotated[BaseService, Depends(neural_model_service)]
):
    # TODO: implement deleting from models dir
    return await service.delete(id)


@router.post("/predictions/{genus}")
async def get_predictions(
    genus: str,
    image: UploadFile,
    n_model_service: Annotated[BaseService, Depends(neural_model_service)],
    plant_service_: Annotated[BaseService, Depends(plant_service)],
):
    # get plants of the genus
    plants = [
        (plant.id, plant.species)
        for plant in await plant_service_.search_by_field("genus", genus)
    ]
    # get paths to models
    models = {}
    for id, species in plants:
        model_list = await n_model_service.search_by_field("plant_id", id)
        if len(model_list):
            models[species] = model_list[0].model_name

    # get probabilities
    probabilities: list[dict[str, float]] = []
    m = list(models.items())
    m.reverse()
    img_data: bytes = image.file.read()
    for species, model_path in m:
        model = load_model(model_path)
        img_tensor = torch.frombuffer(buffer=img_data, dtype=torch.uint8)
        image_t = decode_image(img_tensor, mode=ImageReadMode.RGB)
        probabilities.append(
            {"classifier": species, "probability": get_prediction(image_t, model)}
        )
        image.file.seek(0)

    return JSONResponse(probabilities)
