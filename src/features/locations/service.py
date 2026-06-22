from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.features.locations.repository import (
    AddressRepo,
    CountryRepo,
    DistrictRepo,
    HouseNumberRepo,
    LocationRepo,
    RegionRepo,
    SettlementRepo,
    SettlementTypeRepo,
    StreetRepo,
)
from src.shared.database import get_db
from src.shared.service import BaseService

# ── Repo factory helpers ──────────────────────────────────────


async def get_country_repo(s: AsyncSession = Depends(get_db)) -> CountryRepo:
    return CountryRepo(s)


async def get_region_repo(s: AsyncSession = Depends(get_db)) -> RegionRepo:
    return RegionRepo(s)


async def get_district_repo(s: AsyncSession = Depends(get_db)) -> DistrictRepo:
    return DistrictRepo(s)


async def get_settlement_type_repo(
    s: AsyncSession = Depends(get_db),
) -> SettlementTypeRepo:
    return SettlementTypeRepo(s)


async def get_settlement_repo(s: AsyncSession = Depends(get_db)) -> SettlementRepo:
    return SettlementRepo(s)


async def get_street_repo(s: AsyncSession = Depends(get_db)) -> StreetRepo:
    return StreetRepo(s)


async def get_house_number_repo(s: AsyncSession = Depends(get_db)) -> HouseNumberRepo:
    return HouseNumberRepo(s)


async def get_address_repo(s: AsyncSession = Depends(get_db)) -> AddressRepo:
    return AddressRepo(s)


async def get_location_repo(s: AsyncSession = Depends(get_db)) -> LocationRepo:
    return LocationRepo(s)


# ── Services ──────────────────────────────────────────────────


class CountryService(BaseService[CountryRepo]):
    def __init__(self, repo: CountryRepo):
        self._repo = repo


class RegionService(BaseService[RegionRepo]):
    def __init__(self, repo: RegionRepo):
        self._repo = repo


class DistrictService(BaseService[DistrictRepo]):
    def __init__(self, repo: DistrictRepo):
        self._repo = repo


class SettlementTypeService(BaseService[SettlementTypeRepo]):
    def __init__(self, repo: SettlementTypeRepo):
        self._repo = repo


class SettlementService(BaseService[SettlementRepo]):
    def __init__(self, repo: SettlementRepo):
        self._repo = repo


class StreetService(BaseService[StreetRepo]):
    def __init__(self, repo: StreetRepo):
        self._repo = repo


class HouseNumberService(BaseService[HouseNumberRepo]):
    def __init__(self, repo: HouseNumberRepo):
        self._repo = repo


class AddressService(BaseService[AddressRepo]):
    def __init__(self, repo: AddressRepo):
        self._repo = repo


class LocationService(BaseService[LocationRepo]):
    def __init__(self, repo: LocationRepo):
        self._repo = repo


# ── Service factory helpers ───────────────────────────────────


async def get_country_service(
    repo: CountryRepo = Depends(get_country_repo),
) -> CountryService:
    return CountryService(repo)


async def get_region_service(
    repo: RegionRepo = Depends(get_region_repo),
) -> RegionService:
    return RegionService(repo)


async def get_district_service(
    repo: DistrictRepo = Depends(get_district_repo),
) -> DistrictService:
    return DistrictService(repo)


async def get_settlement_type_service(
    repo: SettlementTypeRepo = Depends(get_settlement_type_repo),
) -> SettlementTypeService:
    return SettlementTypeService(repo)


async def get_settlement_service(
    repo: SettlementRepo = Depends(get_settlement_repo),
) -> SettlementService:
    return SettlementService(repo)


async def get_street_service(
    repo: StreetRepo = Depends(get_street_repo),
) -> StreetService:
    return StreetService(repo)


async def get_house_number_service(
    repo: HouseNumberRepo = Depends(get_house_number_repo),
) -> HouseNumberService:
    return HouseNumberService(repo)


async def get_address_service(
    repo: AddressRepo = Depends(get_address_repo),
) -> AddressService:
    return AddressService(repo)


async def get_location_service(
    repo: LocationRepo = Depends(get_location_repo),
) -> LocationService:
    return LocationService(repo)
