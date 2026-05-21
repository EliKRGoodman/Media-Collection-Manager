"""
Metadata API routes.

These endpoints expose metadata lookup/search behavior to the frontend.

For now, this route only searches MusicBrainz and does not save anything.
Later, we will add an import endpoint that lets the user select one result
and create an Album / CollectionItem from it.
"""

from fastapi import APIRouter, Query
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.models.collection_item import CollectionItem
from app.schemas.metadata import (
    MetadataImportRequest,
    MetadataImportResponse,
)
from app.services.musicbrainz import (
    get_tracks_for_release_group,
    search_release_groups,
)


router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("/search")
def search_metadata(
    query: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=25),
):
    """
    Search MusicBrainz for possible album matches.

    Query parameters:
    - query: album title or search text
    - limit: max number of results to return

    Example:
    /metadata/search?query=ok%20computer
    """

    results = search_release_groups(query=query, limit=limit)

    return {
        "query": query,
        "results": results,
    }

@router.post("/import", response_model=MetadataImportResponse)
def import_metadata(
    metadata_in: MetadataImportRequest,
    db: Session = Depends(get_db),
):
    """
    Import a selected metadata result into the local database.

    Workflow:
    1. Reuse or create Artist
    2. Reuse or create Album
    3. Create new CollectionItem

    This supports:
    - duplicate owned copies,
    - shared album metadata,
    - and user-managed collection data.
    """

    #
    # ARTIST
    #

    # Attempt to reuse an existing artist first.
    artist = db.scalar(
        select(Artist).where(
            Artist.name == metadata_in.artist_name
        )
    )

    # Create artist if missing.
    if artist is None:
        artist = Artist(
            name=metadata_in.artist_name
        )

        db.add(artist)
        db.flush()

    #
    # ALBUM
    #

    # Attempt to reuse existing album metadata.
    album = db.scalar(
        select(Album).where(
            Album.title == metadata_in.album_title,
            Album.artist_id == artist.id,
        )
    )

    # Create album if missing.
    if album is None:
        album = Album(
            title=metadata_in.album_title,
            release_year=metadata_in.release_year,
            genre=metadata_in.genre,
            artist_id=artist.id,
        )

        db.add(album)
        db.flush()

    #
    # COLLECTION ITEM
    #

    # Always create a new owned copy.
    #
    # This supports:
    # - duplicate owned copies,
    # - different conditions,
    # - different locations,
    # - different notes/ratings.
    item = CollectionItem(
        album_id=album.id,
        condition=metadata_in.condition,
        notes=metadata_in.notes,
        location=metadata_in.location,
        album_rating=metadata_in.album_rating,
    )

    db.add(item)

    db.commit()

    db.refresh(item)

    return MetadataImportResponse(
        artist_id=artist.id,
        album_id=album.id,
        collection_item_id=item.id,
        artist_name=artist.name,
        album_title=album.title,
    )

@router.get("/musicbrainz/release-groups/{release_group_id}/tracks")
def get_musicbrainz_tracks(release_group_id: str):
    """
    Preview tracks for a selected MusicBrainz release group.

    This endpoint does not save anything.
    It lets the frontend show the user a tracklist before import.
    """

    tracks = get_tracks_for_release_group(release_group_id)

    return {
        "release_group_id": release_group_id,
        "tracks": tracks,
    }