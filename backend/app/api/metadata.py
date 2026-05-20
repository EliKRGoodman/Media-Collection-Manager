"""
Metadata API routes.

These endpoints expose metadata lookup/search behavior to the frontend.

For now, this route only searches MusicBrainz and does not save anything.
Later, we will add an import endpoint that lets the user select one result
and create an Album / CollectionItem from it.
"""

from fastapi import APIRouter, Query

from app.services.musicbrainz import search_release_groups


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