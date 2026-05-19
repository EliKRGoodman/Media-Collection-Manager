from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CollectionItemCreate(BaseModel):
    artist_name: str = Field(min_length=1, max_length=255)
    album_title: str = Field(min_length=1, max_length=255)
    release_year: int | None = None
    genre: str | None = None
    condition: str | None = None
    notes: str | None = None
    location: str | None = None
    price: Decimal | None = None
    album_rating: int | None = Field(default=None, ge=1, le=10)


class CollectionItemRead(BaseModel):
    id: int
    artist_name: str
    album_title: str
    release_year: int | None
    genre: str | None
    condition: str | None
    notes: str | None
    location: str | None
    price: Decimal | None
    album_rating: int | None
    date_added: datetime

    model_config = {"from_attributes": True}