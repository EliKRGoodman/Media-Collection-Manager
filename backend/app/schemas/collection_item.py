from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TrackCreate(BaseModel):
    """
    Incoming API shape for a track when creating a collection item.

    These tracks belong to the album being created or reused.
    """

    title: str = Field(min_length=1, max_length=255)
    track_number: int | None = None
    runtime_seconds: int | None = None
    rating: int | None = Field(default=None, ge=1, le=10)


class TrackRead(BaseModel):
    """
    Outgoing API shape for a track.

    This is what the API returns to clients.
    """

    id: int
    title: str
    track_number: int | None
    runtime_seconds: int | None
    rating: int | None

    model_config = {"from_attributes": True}


class CollectionItemCreate(BaseModel):
    """
    Incoming API shape for creating an owned album copy.

    This combines:
    - artist-level input,
    - album-level input,
    - collection-item-specific input,
    - optional tags,
    - optional tracks.
    """

    artist_name: str = Field(min_length=1, max_length=255)
    album_title: str = Field(min_length=1, max_length=255)
    release_year: int | None = None
    genre: str | None = None
    image_url: str | None = None
    condition: str | None = None
    notes: str | None = None
    location_name: str | None = None
    price: Decimal | None = None
    album_rating: int | None = Field(default=None, ge=1, le=10)
    tags: list[str] = []
    tracks: list[TrackCreate] = []

class CollectionItemUpdate(BaseModel):
    """
    Incoming API shape for editing an existing collection item.

    All fields are optional because PATCH means:
    "only update the fields the user provided."
    """

    condition: str | None = None
    notes: str | None = None
    location_name: str | None = None
    price: Decimal | None = None
    album_rating: int | None = Field(default=None, ge=1, le=10)

    # Optional full tag replacement.
    #
    # If tags is omitted, tags are unchanged.
    # If tags is provided, the item's tags are replaced with this list.
    tags: list[str] | None = None
    
class CollectionItemRead(BaseModel):
    """
    Outgoing API shape for an owned album copy.

    This flattens some related data for convenience:
    - artist name comes from Artist
    - album title/release year/genre come from Album
    - tags come from Tag
    - tracks come from Track
    """

    id: int
    artist_name: str
    album_title: str
    release_year: int | None
    genre: str | None
    image_url: str | None
    condition: str | None
    notes: str | None
    location_name: str | None
    price: Decimal | None
    album_rating: int | None
    date_added: datetime
    tags: list[str]
    tracks: list[TrackRead]
    

    model_config = {"from_attributes": True}