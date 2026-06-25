from typing import Annotated

from pydantic import BaseModel, Field
from src.shared.schemas import BaseSchema
from src.shared.types import PyUUID


class GenusCreate(BaseModel):
    latin_name: Annotated[str, Field(min_length=1, max_length=150)]
    russian_name: str | None = None


class GenusUpdate(BaseModel):
    latin_name: Annotated[str | None, Field(min_length=1, max_length=150)] = None
    russian_name: str | None = None


class GenusRead(BaseSchema):
    genus_id: PyUUID = Field(validation_alias="id")
    latin_name: str
    russian_name: str | None


class SpeciesCreate(BaseModel):
    latin_name: Annotated[str, Field(min_length=1, max_length=150)]
    russian_name: str | None = None
    genus_id: PyUUID


class SpeciesUpdate(BaseModel):
    latin_name: Annotated[str | None, Field(min_length=1, max_length=150)] = None
    russian_name: str | None = None
    genus_id: PyUUID | None = None


class GenusNested(BaseSchema):
    genus_id: PyUUID = Field(validation_alias="id")
    latin_name: str


class SpeciesRead(BaseSchema):
    species_id: PyUUID = Field(validation_alias="id")
    latin_name: str
    russian_name: str | None
    genus: GenusNested | None = None
