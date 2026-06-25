"""Shared schema base class with ORM compatibility."""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base for all response schemas.

    Enables ``from_attributes=True`` so FastAPI can serialize SQLAlchemy
    ORM objects directly via ``response_model``.
    """

    model_config = ConfigDict(from_attributes=True)
