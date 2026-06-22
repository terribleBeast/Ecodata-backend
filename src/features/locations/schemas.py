from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.types import PyUUID

# ── Country ───────────────────────────────────────────────────


class CountryCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]


class CountryUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None


class CountryResponse(BaseModel):
    id: PyUUID
    name: str


# ── Region ────────────────────────────────────────────────────


class RegionCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    country_id: PyUUID


class RegionUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    country_id: PyUUID | None = None


class RegionResponse(BaseModel):
    id: PyUUID
    name: str
    country_id: PyUUID


# ── District ──────────────────────────────────────────────────


class DistrictCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    region_id: PyUUID


class DistrictUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    region_id: PyUUID | None = None


class DistrictResponse(BaseModel):
    id: PyUUID
    name: str
    region_id: PyUUID


# ── SettlementType ────────────────────────────────────────────


class SettlementTypeCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]


class SettlementTypeUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None


class SettlementTypeResponse(BaseModel):
    id: PyUUID
    name: str


# ── Settlement ────────────────────────────────────────────────


class SettlementCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]
    district_id: PyUUID
    settlement_type_id: PyUUID


class SettlementUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    district_id: PyUUID | None = None
    settlement_type_id: PyUUID | None = None


class SettlementResponse(BaseModel):
    id: PyUUID
    name: str
    district_id: PyUUID
    settlement_type_id: PyUUID


# ── Street ────────────────────────────────────────────────────


class StreetCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=255)]


class StreetUpdate(BaseModel):
    name: Annotated[str | None, Field(min_length=1, max_length=255)] = None


class StreetResponse(BaseModel):
    id: PyUUID
    name: str


# ── HouseNumber ───────────────────────────────────────────────


class HouseNumberCreate(BaseModel):
    number: Annotated[str, Field(min_length=1, max_length=50)]


class HouseNumberUpdate(BaseModel):
    number: Annotated[str | None, Field(min_length=1, max_length=50)] = None


class HouseNumberResponse(BaseModel):
    id: PyUUID
    number: str


# ── Address ───────────────────────────────────────────────────


class AddressCreate(BaseModel):
    house_number_id: PyUUID
    street_id: PyUUID
    settlement_id: PyUUID


class AddressUpdate(BaseModel):
    house_number_id: PyUUID | None = None
    street_id: PyUUID | None = None
    settlement_id: PyUUID | None = None


class AddressResponse(BaseModel):
    id: PyUUID
    house_number_id: PyUUID
    street_id: PyUUID
    settlement_id: PyUUID


# ── Location ──────────────────────────────────────────────────


class LocationCreate(BaseModel):
    address_id: PyUUID | None = None
    latitude: Annotated[
        Decimal | None, Field(ge=-90, le=90, max_digits=9, decimal_places=6)
    ] = None
    longitude: Annotated[
        Decimal | None, Field(ge=-180, le=180, max_digits=9, decimal_places=6)
    ] = None
    description: str | None = None


class LocationUpdate(BaseModel):
    address_id: PyUUID | None = None
    latitude: Annotated[
        Decimal | None, Field(ge=-90, le=90, max_digits=9, decimal_places=6)
    ] = None
    longitude: Annotated[
        Decimal | None, Field(ge=-180, le=180, max_digits=9, decimal_places=6)
    ] = None
    description: str | None = None


class LocationResponse(BaseModel):
    id: PyUUID
    address_id: PyUUID | None
    latitude: Decimal | None
    longitude: Decimal | None
    description: str | None
