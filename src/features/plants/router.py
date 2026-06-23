from fastapi import APIRouter, Depends
from src.features.plants.schemas import (
    LeafBladeTypeCreate,
    LeafBladeTypeResponse,
    LeafBladeTypeUpdate,
    LocationOnPlantCreate,
    LocationOnPlantResponse,
    LocationOnPlantUpdate,
    PlantCreate,
    PlantDescriptionCreate,
    PlantDescriptionResponse,
    PlantDescriptionUpdate,
    PlantLifeFormCreate,
    PlantLifeFormResponse,
    PlantLifeFormUpdate,
    PlantResponse,
    PlantUpdate,
    SideOfTheWorldCreate,
    SideOfTheWorldResponse,
    SideOfTheWorldUpdate,
)
from src.features.plants.service import (
    LeafBladeTypeService,
    LocationOnPlantService,
    PlantDescriptionService,
    PlantLifeFormService,
    PlantService,
    SideOfTheWorldService,
    get_leaf_blade_type_service,
    get_location_on_plant_service,
    get_plant_description_service,
    get_plant_life_form_service,
    get_plant_service,
    get_side_of_the_world_service,
)
from src.shared.types import PyUUID

# ── Plants ────────────────────────────────────────────────────

plants_router = APIRouter(prefix="/plants", tags=["plants"])


@plants_router.get("/", response_model=list[PlantResponse])
async def plant_list(service=Depends(get_plant_service)):
    return await service.get_all()


@plants_router.get("/{id}", response_model=PlantResponse)
async def plant_get(id: PyUUID, service=Depends(get_plant_service)):
    return await service.get_one(id)


@plants_router.post("/", response_model=PyUUID, status_code=201)
async def plant_create(item: PlantCreate, service=Depends(get_plant_service)):
    return await service.create(item)


@plants_router.patch("/{id}", response_model=PyUUID)
async def plant_update(
    id: PyUUID, item: PlantUpdate, service=Depends(get_plant_service)
):
    return await service.update(id, item)


@plants_router.delete("/{id}", status_code=204)
async def plant_delete(id: PyUUID, service=Depends(get_plant_service)):
    await service.delete(id)


# ── Plant Life Forms ──────────────────────────────────────────

plant_life_forms_router = APIRouter(
    prefix="/plant-life-forms", tags=["plant-life-forms"]
)


@plant_life_forms_router.get("/", response_model=list[PlantLifeFormResponse])
async def life_form_list(service=Depends(get_plant_life_form_service)):
    return await service.get_all()


@plant_life_forms_router.get("/{id}", response_model=PlantLifeFormResponse)
async def life_form_get(id: PyUUID, service=Depends(get_plant_life_form_service)):
    return await service.get_one(id)


@plant_life_forms_router.post("/", response_model=PyUUID, status_code=201)
async def life_form_create(
    item: PlantLifeFormCreate, service=Depends(get_plant_life_form_service)
):
    return await service.create(item)


@plant_life_forms_router.patch("/{id}", response_model=PyUUID)
async def life_form_update(
    id: PyUUID,
    item: PlantLifeFormUpdate,
    service=Depends(get_plant_life_form_service),
):
    return await service.update(id, item)


@plant_life_forms_router.delete("/{id}", status_code=204)
async def life_form_delete(id: PyUUID, service=Depends(get_plant_life_form_service)):
    await service.delete(id)


# ── Leaf Blade Types ──────────────────────────────────────────

leaf_blade_types_router = APIRouter(
    prefix="/leaf-blade-types", tags=["leaf-blade-types"]
)


@leaf_blade_types_router.get("/", response_model=list[LeafBladeTypeResponse])
async def blade_type_list(service=Depends(get_leaf_blade_type_service)):
    return await service.get_all()


@leaf_blade_types_router.get("/{id}", response_model=LeafBladeTypeResponse)
async def blade_type_get(id: PyUUID, service=Depends(get_leaf_blade_type_service)):
    return await service.get_one(id)


@leaf_blade_types_router.post("/", response_model=PyUUID, status_code=201)
async def blade_type_create(
    item: LeafBladeTypeCreate, service=Depends(get_leaf_blade_type_service)
):
    return await service.create(item)


@leaf_blade_types_router.patch("/{id}", response_model=PyUUID)
async def blade_type_update(
    id: PyUUID,
    item: LeafBladeTypeUpdate,
    service=Depends(get_leaf_blade_type_service),
):
    return await service.update(id, item)


@leaf_blade_types_router.delete("/{id}", status_code=204)
async def blade_type_delete(id: PyUUID, service=Depends(get_leaf_blade_type_service)):
    await service.delete(id)


# ── Plant Descriptions ────────────────────────────────────────

plant_descriptions_router = APIRouter(
    prefix="/plant-descriptions", tags=["plant-descriptions"]
)


@plant_descriptions_router.get("/", response_model=list[PlantDescriptionResponse])
async def description_list(service=Depends(get_plant_description_service)):
    return await service.get_all()


@plant_descriptions_router.get("/{id}", response_model=PlantDescriptionResponse)
async def description_get(id: PyUUID, service=Depends(get_plant_description_service)):
    return await service.get_one(id)


@plant_descriptions_router.post("/", response_model=PyUUID, status_code=201)
async def description_create(
    item: PlantDescriptionCreate,
    service=Depends(get_plant_description_service),
):
    return await service.create(item)


@plant_descriptions_router.patch("/{id}", response_model=PyUUID)
async def description_update(
    id: PyUUID,
    item: PlantDescriptionUpdate,
    service=Depends(get_plant_description_service),
):
    return await service.update(id, item)


@plant_descriptions_router.delete("/{id}", status_code=204)
async def description_delete(
    id: PyUUID, service=Depends(get_plant_description_service)
):
    await service.delete(id)


# ── Side of the World ─────────────────────────────────────────

side_of_the_world_router = APIRouter(
    prefix="/side-of-the-world", tags=["side-of-the-world"]
)


@side_of_the_world_router.get("/", response_model=list[SideOfTheWorldResponse])
async def side_list(service=Depends(get_side_of_the_world_service)):
    return await service.get_all()


@side_of_the_world_router.get("/{id}", response_model=SideOfTheWorldResponse)
async def side_get(id: PyUUID, service=Depends(get_side_of_the_world_service)):
    return await service.get_one(id)


@side_of_the_world_router.post("/", response_model=PyUUID, status_code=201)
async def side_create(
    item: SideOfTheWorldCreate, service=Depends(get_side_of_the_world_service)
):
    return await service.create(item)


@side_of_the_world_router.patch("/{id}", response_model=PyUUID)
async def side_update(
    id: PyUUID,
    item: SideOfTheWorldUpdate,
    service=Depends(get_side_of_the_world_service),
):
    return await service.update(id, item)


@side_of_the_world_router.delete("/{id}", status_code=204)
async def side_delete(id: PyUUID, service=Depends(get_side_of_the_world_service)):
    await service.delete(id)


# ── Location on Plant ─────────────────────────────────────────

location_on_plant_router = APIRouter(
    prefix="/location-on-plant", tags=["location-on-plant"]
)


@location_on_plant_router.get("/", response_model=list[LocationOnPlantResponse])
async def loc_plant_list(service=Depends(get_location_on_plant_service)):
    return await service.get_all()


@location_on_plant_router.get("/{id}", response_model=LocationOnPlantResponse)
async def loc_plant_get(id: PyUUID, service=Depends(get_location_on_plant_service)):
    return await service.get_one(id)


@location_on_plant_router.post("/", response_model=PyUUID, status_code=201)
async def loc_plant_create(
    item: LocationOnPlantCreate, service=Depends(get_location_on_plant_service)
):
    return await service.create(item)


@location_on_plant_router.patch("/{id}", response_model=PyUUID)
async def loc_plant_update(
    id: PyUUID,
    item: LocationOnPlantUpdate,
    service=Depends(get_location_on_plant_service),
):
    return await service.update(id, item)


@location_on_plant_router.delete("/{id}", status_code=204)
async def loc_plant_delete(id: PyUUID, service=Depends(get_location_on_plant_service)):
    await service.delete(id)
