from fastapi import APIRouter

from .neural_models import router as neural_models_router
from .plant import router as plant_router

router = APIRouter()

router.include_router(plant_router)
router.include_router(neural_models_router)
