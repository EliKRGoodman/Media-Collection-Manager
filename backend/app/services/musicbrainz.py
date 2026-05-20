"""
MusicBrainz service layer.

This module is responsible for talking to the external MusicBrainz API.

Important architecture note:
API route files should not directly contain external API logic.
Keeping this in a service layer makes the code easier to test, replace,
and expand later when we add Discogs, Wikipedia, Spotify, etc.
"""

import httpx


MUSICBRAINZ_BASE_URL = "https://musicbrainz.org/ws/2"


def search_release_groups(query: str, limit: int = 10) -> list[dict]:
    """
    Search MusicBrainz release groups by text query.

    In MusicBrainz terminology, a release group is close to our current
    V1 concept of an album as a general work, rather than a specific
    pressing, country release, or edition.

    Args:
        query:
            User-entered album search text.
            Example: "OK Computer"

        limit:
            Maximum number of matches to return.

    Returns:
        A simplified list of album-like matches for the API layer.
    """

    # MusicBrainz asks API clients to identify themselves with User-Agent.
    # This is good API citizenship and helps external services contact
    # developers if a client causes problems.
    headers = {
        "User-Agent": "MediaCollectionManager/0.1 (local development)"
    }

    # Search endpoint:
    # /ws/2/release-group
    #
    # fmt=json requests JSON instead of XML.
    params = {
        "query": query,
        "fmt": "json",
        "limit": limit,
    }

    response = httpx.get(
        f"{MUSICBRAINZ_BASE_URL}/release-group",
        params=params,
        headers=headers,
        timeout=10.0,
    )

    # Raise an exception if MusicBrainz returns an error status.
    # Later we can replace this with nicer user-facing error handling.
    response.raise_for_status()

    data = response.json()

    results = []

    for release_group in data.get("release-groups", []):
        artist_credit = release_group.get("artist-credit", [])

        artist_name = None
        if artist_credit:
            artist_name = artist_credit[0].get("name")

        results.append(
            {
                "musicbrainz_id": release_group.get("id"),
                "title": release_group.get("title"),
                "artist_name": artist_name,
                "first_release_date": release_group.get("first-release-date"),
                "primary_type": release_group.get("primary-type"),
                "score": release_group.get("score"),
            }
        )

    return results