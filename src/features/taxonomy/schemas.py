from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.types import PyUUID


class GenusCreate(BaseModel):
    latin_name: Annotated[str, Field(min_length=1, max_length=150)]
    russian_name: str | None = None


class GenusUpdate(BaseModel):
    latin_name: Annotated[str | None, Field(min_length=1, max_length=150)] = None
    russian_name: str | None = None


class GenusRead(BaseModel):
    id: PyUUID
    latin_name: str
    russian_name: str | None

    model_config = {"from_attributes": True}


class SpeciesCreate(BaseModel):
    latin_name: Annotated[str, Field(min_length=1, max_length=150)]
    russian_name: str | None = None
    genus_id: PyUUID


class SpeciesUpdate(BaseModel):
    latin_name: Annotated[str | None, Field(min_length=1, max_length=150)] = None
    russian_name: str | None = None
    genus_id: PyUUID | None = None


class SpeciesRead(BaseModel):
    id: PyUUID
    latin_name: str
    russian_name: str | None
    genus_id: PyUUID

    model_config = {"from_attributes": True}
