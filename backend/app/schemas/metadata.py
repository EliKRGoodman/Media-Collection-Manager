"""
Pydantic schemas for metadata import/search workflows.
"""

from pydantic import BaseModel, Field


class MusicBrainzTrackRead(BaseModel):
    """
    Track data returned from MusicBrainz before importing.

    This is not a database model.
    It is the API response shape for previewing external metadata.
    """

    title: str | None
    track_number: int | None
    runtime_seconds: int | None


class MetadataImportTrack(BaseModel):
    """
    Track data included when importing metadata.

    This allows the frontend to:
    1. search MusicBrainz,
    2. preview tracks,
    3. send selected track data into the import endpoint.
    """

    title: str = Field(min_length=1)
    track_number: int | None = None
    runtime_seconds: int | None = None
    rating: int | None = Field(default=None, ge=1, le=10)


class MetadataImportRequest(BaseModel):
    """
    Request body for importing a selected metadata result.

    This represents the user's chosen metadata match plus
    optional collection-specific information.
    """

    artist_name: str = Field(min_length=1)
    album_title: str = Field(min_length=1)

    release_year: int | None = None
    genre: str | None = None

    condition: str | None = None
    notes: str | None = None
    location: str | None = None
    album_rating: int | None = Field(default=None, ge=1, le=10)

    tracks: list[MetadataImportTrack] = []


class MetadataImportResponse(BaseModel):
    """
    Response returned after successful metadata import.
    """

    artist_id: int
    album_id: int
    collection_item_id: int

    artist_name: str
    album_title: str
    tracks_created: int