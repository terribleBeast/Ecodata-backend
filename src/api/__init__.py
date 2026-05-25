from fastapi import APIRouter

from .log import router as log_router
from .neural_models import router as neural_models_router
from .plant import router as plant_router

router = APIRouter()

router.include_router(plant_router)
router.include_router(neural_models_router)
router.include_router(log_router)
