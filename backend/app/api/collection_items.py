from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

from app.db.deps import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.models.collection_item import CollectionItem
from app.schemas.collection_item import CollectionItemCreate, CollectionItemRead
from app.models.tag import Tag
from app.models.track import Track
from app.schemas.collection_item import CollectionItemCreate, CollectionItemRead, TrackRead

router = APIRouter(prefix="/collection-items", tags=["collection items"])


@router.post("/", response_model=CollectionItemRead)
def create_collection_item(
    item_in: CollectionItemCreate,
    db: Session = Depends(get_db),
):
    artist = db.scalar(
        select(Artist).where(Artist.name == item_in.artist_name)
    )

    if artist is None:
        artist = Artist(name=item_in.artist_name)
        db.add(artist)
        db.flush()

    album = db.scalar(
        select(Album).where(
            Album.title == item_in.album_title,
            Album.artist_id == artist.id,
        )
    )

    if album is None:
        album = Album(
            title=item_in.album_title,
            release_year=item_in.release_year,
            genre=item_in.genre,
            artist_id=artist.id,
        )
        db.add(album)
        db.flush()

    item = CollectionItem(
        album_id=album.id,
        condition=item_in.condition,
        notes=item_in.notes,
        location=item_in.location,
        price=item_in.price,
        album_rating=item_in.album_rating,
    )

    # If this is a brand-new album, attach any incoming tracks to it.
    #
    # Important V1 behavior:
    # If the album already exists, we do NOT blindly add tracks again.
    # This prevents duplicate tracklists when adding multiple owned copies
    # of the same album.
    if not album.tracks:
        for track_in in item_in.tracks:
            track = Track(
                album_id=album.id,
                title=track_in.title,
                track_number=track_in.track_number,
                runtime_seconds=track_in.runtime_seconds,
                rating=track_in.rating,
            )
            db.add(track)

    tag_names = {tag.strip() for tag in item_in.tags if tag.strip()}

    for tag_name in tag_names:
        tag = db.scalar(select(Tag).where(Tag.name == tag_name))

        if tag is None:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.flush()

        item.tags.append(tag)

    db.add(item)
    db.commit()
    db.refresh(item)

    return CollectionItemRead(
        id=item.id,
        artist_name=artist.name,
        album_title=album.title,
        release_year=album.release_year,
        genre=album.genre,
        condition=item.condition,
        notes=item.notes,
        location=item.location,
        price=item.price,
        album_rating=item.album_rating,
        date_added=item.date_added,
        tags=[tag.name for tag in item.tags],
        tracks=[
            TrackRead.model_validate(track)
            for track in album.tracks
        ],
    )


@router.get("/", response_model=list[CollectionItemRead])
def list_collection_items(
    # Optional genre filter.
    #
    # Example:
    # /collection-items/?genre=Electronic
    genre: str | None = Query(default=None),

    # Optional tag filter.
    #
    # Example:
    # /collection-items/?tag=favorite
    tag: str | None = Query(default=None),

    db: Session = Depends(get_db),
):
    """
    Return collection items with optional filtering.

    Supported filters:
    - genre
    - tag

    Filters can be combined later as the API evolves.
    """

    # Start with a base query selecting collection items.
    query = select(CollectionItem)

    # Filter by album genre if provided.
    #
    # Because genre lives on Album, we join Album.
    if genre:
        query = (
            query
            .join(CollectionItem.album)
            .where(Album.genre.ilike(f"%{genre}%"))
        )

    # Filter by tag name if provided.
    #
    # Because tags are many-to-many, we join through
    # the CollectionItem.tags relationship.
    if tag:
        query = (
            query
            .join(CollectionItem.tags)
            .where(Tag.name.ilike(f"%{tag}%"))
        )

    # Execute query and return ORM objects.
    items = db.scalars(query).unique().all()

    return [
        CollectionItemRead(
            id=item.id,
            artist_name=item.album.artist.name,
            album_title=item.album.title,
            release_year=item.album.release_year,
            genre=item.album.genre,
            condition=item.condition,
            notes=item.notes,
            location=item.location,
            price=item.price,
            album_rating=item.album_rating,
            date_added=item.date_added,

            # Convert Tag ORM objects into simple string names.
            tags=[
                tag.name
                for tag in item.tags
            ],

            # Convert Track ORM objects into API response schemas.
            tracks=[
                TrackRead.model_validate(track)
                for track in item.album.tracks
            ],
        )
        for item in items
    ]