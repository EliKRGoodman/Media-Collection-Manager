"""
Pydantic schemas for Location API operations.
"""

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    """
    Incoming API shape for creating a location.
    """

    name: str = Field(min_length=1, max_length=255)

    # Optional capacity limit.
    #
    # Example:
    # Shelf A holds 50 records.
    capacity: int | None = Field(default=None, ge=1)


class LocationRead(BaseModel):
    """
    Outgoing API shape for locations.
    """

    id: int
    name: str
    capacity: int | None

    model_config = {"from_attributes": True}