import asyncio
from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from src.features.analyzer.engine import (
    async_get_prediction,
    flush_evictions,
    model_cache,
)
from src.features.analyzer.schemas import NeuralModelCreate, NeuralModelResponse
from src.features.analyzer.service import (
    NeuralModelService,
    get_neural_model_service,
)
from src.features.files.service import FileService, get_file_service
from src.features.taxonomy.schemas import SpeciesRead
from src.features.taxonomy.service import SpeciesService, get_species_service
from src.shared.rustfs import rustfs
from src.shared.types import PyUUID
from starlette.status import HTTP_404_NOT_FOUND

router = APIRouter(prefix="/analyzer", tags=["analyzer"])


# ── CRUD ─────────────────────────────────────────────────────────────


@router.get(
    "/available-species/{genus_id}",
    response_model=list[SpeciesRead],
)
async def available_species_for_models(
    genus_id: PyUUID,
    neural_model_service: Annotated[
        NeuralModelService, Depends(get_neural_model_service)
    ],
    species_service: Annotated[SpeciesService, Depends(get_species_service)],
    file_service: Annotated[FileService, Depends(get_file_service)],
):
    species_list = await species_service.search_by_field("genus_id", genus_id)

    available_species = []

    for species in species_list:
        neural_models = await neural_model_service.search_by_field(
            "species_id",
            species.id,
        )

        active_classifier_models = [
            model
            for model in neural_models
            if model.is_active and model.model_type == "species_classifier"
        ]

        if not active_classifier_models:
            continue

        model = active_classifier_models[0]
        file_record = await file_service.get_one(model.file_id)

        if file_record is None:
            continue

        available_species.append(species)

    return available_species


@router.get("/models", response_model=list[NeuralModelResponse])
async def neural_model_list(
    neural_model_service: Annotated[
        NeuralModelService, Depends(get_neural_model_service)
    ],
    species_service: Annotated[SpeciesService, Depends(get_species_service)],
    genus_id: PyUUID | None = None,
):
    if genus_id:
        species_ids = list(
            map(
                lambda item: item.id,
                list(await species_service.get_by_genus(genus_id)),
            )
        )
        if not species_ids:
            raise HTTPException(HTTP_404_NOT_FOUND)
        result = await neural_model_service.get_by_species(species_ids)
        if not result:
            raise HTTPException(HTTP_404_NOT_FOUND)
        return result
    return await neural_model_service.get_all()


@router.get("/models/{id}", response_model=NeuralModelResponse)
async def neural_model_get(
    id: PyUUID,
    service: Annotated[NeuralModelService, Depends(get_neural_model_service)],
):
    return await service.get_one(id)


@router.post("/models", response_model=PyUUID, status_code=201)
async def create_neural_model(
    body: NeuralModelCreate,
    service: Annotated[NeuralModelService, Depends(get_neural_model_service)],
):
    """Register a neural model from a previously uploaded file (RustFS)."""
    return await service.create(body)


@router.delete("/models/{id}", status_code=204)
async def delete_neural_model(
    id: PyUUID,
    service: Annotated[NeuralModelService, Depends(get_neural_model_service)],
):
    await service.delete(id)


# ── Inference ────────────────────────────────────────────────────────


@router.post("/predictions/{genus_id}")
async def get_predictions(
    genus_id: str,
    image: UploadFile,
    neural_model_service: Annotated[
        NeuralModelService, Depends(get_neural_model_service)
    ],
    species_service: Annotated[SpeciesService, Depends(get_species_service)],
    file_service: Annotated[FileService, Depends(get_file_service)],
):
    # 1. Look up all plant species for this genus
    species_list = [
        (item.id, item.latin_name)
        for item in await species_service.search_by_field("genus_id", genus_id)
    ]

    # 2. Build model map: species → (model_key, loader)
    model_loaders: dict[str, tuple[str, Callable[[], Coroutine[Any, Any, bytes]]]] = {}
    for species_id, species_name in species_list:
        neural_models = await neural_model_service.search_by_field(
            "species_id", species_id
        )
        if neural_models:
            nm = neural_models[0]
            file_record = await file_service.get_one(nm.file_id)
            if file_record is None:
                continue

            model_key = str(nm.id)

            async def make_loader(bucket: str, key: str):
                async def _loader():
                    return await rustfs.get_object(bucket, key)

                return _loader

            loader = await make_loader(
                str(file_record.bucket), str(file_record.object_key)
            )
            model_loaders[species_name] = (model_key, loader)

    if not model_loaders:
        return JSONResponse(
            {"message": f"No models found for genus '{genus_id}'"},
            status_code=404,
        )

    # 3. Read image bytes once
    img_data = await image.read()

    # 4. Run inference per species
    async def predict_one(species: str, model_key: str, loader):
        model = await model_cache.get(model_key, loader)
        probability = await async_get_prediction(img_data, model)
        return {"classifier": species, "probability": probability}

    tasks = [
        predict_one(species, key, loader)
        for species, (key, loader) in model_loaders.items()
    ]
    probabilities = await asyncio.gather(*tasks)

    flush_evictions()
    return JSONResponse({"data": probabilities})
