"""
Pydantic schemas for metadata import/search workflows.

These schemas define:
- incoming metadata import requests,
- outgoing import responses,
- and future external metadata structures.
"""

from pydantic import BaseModel, Field


class MetadataImportRequest(BaseModel):
    """
    Request body for importing a selected metadata result.

    This represents the user's chosen MusicBrainz match,
    plus optional collection-specific information.
    """

    artist_name: str = Field(min_length=1)
    album_title: str = Field(min_length=1)

    release_year: int | None = None
    genre: str | None = None

    # Optional collection-item fields
    condition: str | None = None
    notes: str | None = None
    location: str | None = None
    album_rating: int | None = Field(default=None, ge=1, le=10)


class MetadataImportResponse(BaseModel):
    """
    Response returned after successful metadata import.
    """

    artist_id: int
    album_id: int
    collection_item_id: int

    artist_name: str
    album_title: str