from pydantic import BaseModel, StringConstraints
from src.shared.types import PyUUID
from typing_extensions import Annotated

NameField = Annotated[str, StringConstraints(max_length=40)]


class GenusCreate(BaseModel):
    name: NameField


class GenusUpdate(BaseModel):
    name: NameField


class GenusRead(BaseModel):
    id: PyUUID
    name: str

    model_config = {"from_attributes": True}


class SpeciesCreate(BaseModel):
    name: NameField
    genus_id: PyUUID


class SpeciesUpdate(BaseModel):
    name: NameField | None = None
    genus_id: PyUUID | None = None


class SpeciesRead(BaseModel):
    id: PyUUID
    name: str
    genus_id: PyUUID

    model_config = {"from_attributes": True}
