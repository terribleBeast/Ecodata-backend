from pydantic.main import BaseModel


class PlantCreate(BaseModel):
    genus: str
    species: str
