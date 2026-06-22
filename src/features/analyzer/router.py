import asyncio
from pathlib import Path
from shutil import copyfileobj
from time import time
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from src.features.analyzer.engine import (
    MODELS_DIR,
    async_get_prediction,
    flush_evictions,
    model_cache,
)
from src.features.analyzer.schemas import NeuralModelCreate
from src.features.analyzer.service import (
    NeuralModelService,
    get_neural_model_service,
)
from src.features.taxonomy.service import SpeciesService, get_species_service
from src.shared.types import PyUUID

router = APIRouter(prefix="/analyzer", tags=["analyzer"])


# ── CRUD ─────────────────────────────────────────────────────────────


@router.get("/{genus_id}")
async def neural_model_list(
    neural_model_service: Annotated[
        NeuralModelService, Depends(get_neural_model_service)
    ],
    species_service: Annotated[SpeciesService, Depends(get_species_service)],
    genus_id: Optional[PyUUID] = None,
):
    # if genus_id:
    items = await species_service.get_by_genus(str(genus_id))
    # else:
    #     items = await neural_model_service.get_all()
    return {"data": items}


@router.post("/")
async def create_neural_model(
    service: Annotated[NeuralModelService, Depends(get_neural_model_service)],
    model_file: UploadFile,
    species_id: PyUUID,
):
    model_file_extension = ".pth"

    if Path(str(model_file.filename)).suffix.lower() != model_file_extension:
        return {"message": "The model file must have 'pth' extension"}

    model_name = str(int(time())) + model_file_extension
    path = MODELS_DIR / model_name
    try:
        await service.create(NeuralModelCreate(name=model_name, species_id=species_id))

        with open(path, "wb+") as f:
            copyfileobj(model_file.file, f)

        return {"message": f"The Model is saved with name {path}"}
    except Exception as e:
        return {"message": str(e)}


@router.delete("/{id}")
async def delete_neural_model(
    id: PyUUID,
    service: Annotated[NeuralModelService, Depends(get_neural_model_service)],
):
    return await service.delete(id)


# ── Inference ────────────────────────────────────────────────────────


@router.post("/predictions/{genus_id}")
async def get_predictions(
    genus_id: str,
    image: UploadFile,
    neural_model_service: Annotated[
        NeuralModelService, Depends(get_neural_model_service)
    ],
    get_species_service: Annotated[SpeciesService, Depends(get_species_service)],
):
    probabilities: list[dict[str, str | float]] = []

    # 1. Look up all plant species for this genus
    species_list = [
        (item.id, item.name)
        for item in await get_species_service.search_by_field("genus_id", genus_id)
    ]

    # 2. Find the neural_model model for each species
    models: dict[str, str] = {}
    for species_id, species in species_list:
        model_list = await neural_model_service.search_by_field(
            "species_id", species_id
        )
        if model_list:
            models[species] = model_list[0].name

    if not models:
        return JSONResponse(
            {"message": f"No neural_models found for genus '{genus_id}'"},
            status_code=404,
        )

    # 3. Read image bytes once (async)
    img_data = await image.read()

    # 4. Run inference per species — each prediction runs in a thread-pool
    #    worker so the event loop stays responsive.  Models are cached in
    #    memory after the first load, so subsequent calls are cheap.

    async def predict_one(species: str, model_name: str):
        model = await model_cache.get(model_name)
        probability = await async_get_prediction(img_data, model)
        return {"classifier": species, "probability": probability}

    tasks = [predict_one(species, model_name) for species, model_name in models.items()]

    probabilities = await asyncio.gather(*tasks)

    flush_evictions()
    return JSONResponse({"data": probabilities})
