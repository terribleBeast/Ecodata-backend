from fastapi import APIRouter, Depends
from src.features.locations.schemas import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    CountryCreate,
    CountryResponse,
    CountryUpdate,
    DistrictCreate,
    DistrictResponse,
    DistrictUpdate,
    HouseNumberCreate,
    HouseNumberResponse,
    HouseNumberUpdate,
    LocationCreate,
    LocationResponse,
    LocationUpdate,
    RegionCreate,
    RegionResponse,
    RegionUpdate,
    SettlementCreate,
    SettlementResponse,
    SettlementTypeCreate,
    SettlementTypeResponse,
    SettlementTypeUpdate,
    SettlementUpdate,
    StreetCreate,
    StreetResponse,
    StreetUpdate,
)
from src.features.locations.service import (
    get_address_service,
    get_country_service,
    get_district_service,
    get_house_number_service,
    get_location_service,
    get_region_service,
    get_settlement_service,
    get_settlement_type_service,
    get_street_service,
)
from src.shared.types import PyUUID

# ── Countries ─────────────────────────────────────────────────

countries_router = APIRouter(prefix="/countries", tags=["countries"])


@countries_router.get("/", response_model=list[CountryResponse])
async def country_list(service=Depends(get_country_service)):
    return await service.get_all()


@countries_router.get("/{id}", response_model=CountryResponse)
async def country_get(id: PyUUID, service=Depends(get_country_service)):
    return await service.get_one(id)


@countries_router.post("/", response_model=PyUUID, status_code=201)
async def country_create(item: CountryCreate, service=Depends(get_country_service)):
    return await service.create(item)


@countries_router.patch("/{id}", response_model=PyUUID)
async def country_update(
    id: PyUUID, item: CountryUpdate, service=Depends(get_country_service)
):
    return await service.update(id, item)


@countries_router.delete("/{id}", status_code=204)
async def country_delete(id: PyUUID, service=Depends(get_country_service)):
    await service.delete(id)


# ── Regions ───────────────────────────────────────────────────

regions_router = APIRouter(prefix="/regions", tags=["regions"])


@regions_router.get("/", response_model=list[RegionResponse])
async def region_list(service=Depends(get_region_service)):
    return await service.get_all()


@regions_router.get("/{id}", response_model=RegionResponse)
async def region_get(id: PyUUID, service=Depends(get_region_service)):
    return await service.get_one(id)


@regions_router.post("/", response_model=PyUUID, status_code=201)
async def region_create(item: RegionCreate, service=Depends(get_region_service)):
    return await service.create(item)


@regions_router.patch("/{id}", response_model=PyUUID)
async def region_update(
    id: PyUUID, item: RegionUpdate, service=Depends(get_region_service)
):
    return await service.update(id, item)


@regions_router.delete("/{id}", status_code=204)
async def region_delete(id: PyUUID, service=Depends(get_region_service)):
    await service.delete(id)


# ── Districts ─────────────────────────────────────────────────

districts_router = APIRouter(prefix="/districts", tags=["districts"])


@districts_router.get("/", response_model=list[DistrictResponse])
async def district_list(service=Depends(get_district_service)):
    return await service.get_all()


@districts_router.get("/{id}", response_model=DistrictResponse)
async def district_get(id: PyUUID, service=Depends(get_district_service)):
    return await service.get_one(id)


@districts_router.post("/", response_model=PyUUID, status_code=201)
async def district_create(item: DistrictCreate, service=Depends(get_district_service)):
    return await service.create(item)


@districts_router.patch("/{id}", response_model=PyUUID)
async def district_update(
    id: PyUUID, item: DistrictUpdate, service=Depends(get_district_service)
):
    return await service.update(id, item)


@districts_router.delete("/{id}", status_code=204)
async def district_delete(id: PyUUID, service=Depends(get_district_service)):
    await service.delete(id)


# ── Settlement Types ──────────────────────────────────────────

settlement_types_router = APIRouter(
    prefix="/settlement-types", tags=["settlement-types"]
)


@settlement_types_router.get("/", response_model=list[SettlementTypeResponse])
async def settlement_type_list(service=Depends(get_settlement_type_service)):
    return await service.get_all()


@settlement_types_router.get("/{id}", response_model=SettlementTypeResponse)
async def settlement_type_get(id: PyUUID, service=Depends(get_settlement_type_service)):
    return await service.get_one(id)


@settlement_types_router.post("/", response_model=PyUUID, status_code=201)
async def settlement_type_create(
    item: SettlementTypeCreate, service=Depends(get_settlement_type_service)
):
    return await service.create(item)


@settlement_types_router.patch("/{id}", response_model=PyUUID)
async def settlement_type_update(
    id: PyUUID,
    item: SettlementTypeUpdate,
    service=Depends(get_settlement_type_service),
):
    return await service.update(id, item)


@settlement_types_router.delete("/{id}", status_code=204)
async def settlement_type_delete(
    id: PyUUID, service=Depends(get_settlement_type_service)
):
    await service.delete(id)


# ── Settlements ───────────────────────────────────────────────

settlements_router = APIRouter(prefix="/settlements", tags=["settlements"])


@settlements_router.get("/", response_model=list[SettlementResponse])
async def settlement_list(service=Depends(get_settlement_service)):
    return await service.get_all()


@settlements_router.get("/{id}", response_model=SettlementResponse)
async def settlement_get(id: PyUUID, service=Depends(get_settlement_service)):
    return await service.get_one(id)


@settlements_router.post("/", response_model=PyUUID, status_code=201)
async def settlement_create(
    item: SettlementCreate, service=Depends(get_settlement_service)
):
    return await service.create(item)


@settlements_router.patch("/{id}", response_model=PyUUID)
async def settlement_update(
    id: PyUUID, item: SettlementUpdate, service=Depends(get_settlement_service)
):
    return await service.update(id, item)


@settlements_router.delete("/{id}", status_code=204)
async def settlement_delete(id: PyUUID, service=Depends(get_settlement_service)):
    await service.delete(id)


# ── Streets ───────────────────────────────────────────────────

streets_router = APIRouter(prefix="/streets", tags=["streets"])


@streets_router.get("/", response_model=list[StreetResponse])
async def street_list(service=Depends(get_street_service)):
    return await service.get_all()


@streets_router.get("/{id}", response_model=StreetResponse)
async def street_get(id: PyUUID, service=Depends(get_street_service)):
    return await service.get_one(id)


@streets_router.post("/", response_model=PyUUID, status_code=201)
async def street_create(item: StreetCreate, service=Depends(get_street_service)):
    return await service.create(item)


@streets_router.patch("/{id}", response_model=PyUUID)
async def street_update(
    id: PyUUID, item: StreetUpdate, service=Depends(get_street_service)
):
    return await service.update(id, item)


@streets_router.delete("/{id}", status_code=204)
async def street_delete(id: PyUUID, service=Depends(get_street_service)):
    await service.delete(id)


# ── House Numbers ─────────────────────────────────────────────

house_numbers_router = APIRouter(prefix="/house-numbers", tags=["house-numbers"])


@house_numbers_router.get("/", response_model=list[HouseNumberResponse])
async def house_number_list(service=Depends(get_house_number_service)):
    return await service.get_all()


@house_numbers_router.get("/{id}", response_model=HouseNumberResponse)
async def house_number_get(id: PyUUID, service=Depends(get_house_number_service)):
    return await service.get_one(id)


@house_numbers_router.post("/", response_model=PyUUID, status_code=201)
async def house_number_create(
    item: HouseNumberCreate, service=Depends(get_house_number_service)
):
    return await service.create(item)


@house_numbers_router.patch("/{id}", response_model=PyUUID)
async def house_number_update(
    id: PyUUID, item: HouseNumberUpdate, service=Depends(get_house_number_service)
):
    return await service.update(id, item)


@house_numbers_router.delete("/{id}", status_code=204)
async def house_number_delete(id: PyUUID, service=Depends(get_house_number_service)):
    await service.delete(id)


# ── Addresses ─────────────────────────────────────────────────

addresses_router = APIRouter(prefix="/addresses", tags=["addresses"])


@addresses_router.get("/", response_model=list[AddressResponse])
async def address_list(service=Depends(get_address_service)):
    return await service.get_all()


@addresses_router.get("/{id}", response_model=AddressResponse)
async def address_get(id: PyUUID, service=Depends(get_address_service)):
    return await service.get_one(id)


@addresses_router.post("/", response_model=PyUUID, status_code=201)
async def address_create(item: AddressCreate, service=Depends(get_address_service)):
    return await service.create(item)


@addresses_router.patch("/{id}", response_model=PyUUID)
async def address_update(
    id: PyUUID, item: AddressUpdate, service=Depends(get_address_service)
):
    return await service.update(id, item)


@addresses_router.delete("/{id}", status_code=204)
async def address_delete(id: PyUUID, service=Depends(get_address_service)):
    await service.delete(id)


# ── Locations ─────────────────────────────────────────────────

locations_router = APIRouter(prefix="/locations", tags=["locations"])


@locations_router.get("/", response_model=list[LocationResponse])
async def location_list(service=Depends(get_location_service)):
    return await service.get_all()


@locations_router.get("/{id}", response_model=LocationResponse)
async def location_get(id: PyUUID, service=Depends(get_location_service)):
    return await service.get_one(id)


@locations_router.post("/", response_model=PyUUID, status_code=201)
async def location_create(item: LocationCreate, service=Depends(get_location_service)):
    return await service.create(item)


@locations_router.patch("/{id}", response_model=PyUUID)
async def location_update(
    id: PyUUID, item: LocationUpdate, service=Depends(get_location_service)
):
    return await service.update(id, item)


@locations_router.delete("/{id}", status_code=204)
async def location_delete(id: PyUUID, service=Depends(get_location_service)):
    await service.delete(id)
