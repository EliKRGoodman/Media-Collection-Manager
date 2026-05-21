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

    search: str | None = Query(default=None),
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


    # Optional sort field.
    #
    # Supported values:
    # - artist
    # - release_year
    # - genre
    #
    # Example:
    # /collection-items/?sort_by=artist
    sort_by: str | None = Query(default=None),

    # Sort direction.
    #
    # Supported values:
    # - asc
    # - desc
    #
    # Example:
    # /collection-items/?sort_order=desc
    sort_order: str = Query(default="asc"),

    db: Session = Depends(get_db),
):
    """
    Return collection items with optional filtering and sorting.

    Current filters:
    - genre
    - tag

    Current sorting:
    - artist
    - release_year
    - genre
    """

    # Start with a base query selecting collection items.
    query = select(CollectionItem)

    #
    # FILTERING
    #

    # Filter by album genre.
    #
    # We join Album because genre belongs to Album,
    # not CollectionItem.
    if genre:
        query = (
            query
            .join(CollectionItem.album)
            .where(Album.genre.ilike(f"%{genre}%"))
        )

    # Filter by tag.
    #
    # Tags are many-to-many, so this joins through
    # the CollectionItem.tags relationship.
    if tag:
        query = (
            query
            .join(CollectionItem.tags)
            .where(Tag.name.ilike(f"%{tag}%"))
        )

    # Search by artist name, album title, or track title.
    #
    # This is an early version of "soft search":
    # - case-insensitive
    # - partial matching
    #
    # Later we can add true fuzzy/typo-tolerant search.
    if search:
        query = (
            query
            .join(CollectionItem.album)
            .join(Album.artist)
            .outerjoin(Album.tracks)
            .where(
                Artist.name.ilike(f"%{search}%")
                | Album.title.ilike(f"%{search}%")
                | Track.title.ilike(f"%{search}%")
            )
        )
        
    #
    # SORTING
    #

    # Normalize sort order so the API is case-insensitive.
    sort_order = sort_order.lower()

    # Sort by artist name.
    #
    # Artist name lives on Artist,
    # so we must join through Album -> Artist.
    if sort_by == "artist":

        query = (
            query
            .join(CollectionItem.album)
            .join(Album.artist)
        )

        if sort_order == "desc":
            query = query.order_by(Artist.name.desc())
        else:
            query = query.order_by(Artist.name.asc())

    # Sort by release year.
    elif sort_by == "release_year":

        query = query.join(CollectionItem.album)

        if sort_order == "desc":
            query = query.order_by(Album.release_year.desc())
        else:
            query = query.order_by(Album.release_year.asc())

    # Sort by genre.
    elif sort_by == "genre":

        query = query.join(CollectionItem.album)

        if sort_order == "desc":
            query = query.order_by(Album.genre.desc())
        else:
            query = query.order_by(Album.genre.asc())

    # Sort by album title.
    #
    # Album title lives on Album, so we join from
    # CollectionItem -> Album before ordering.
    elif sort_by in ("album", "album_title"):

        query = query.join(CollectionItem.album)

        if sort_order == "desc":
            query = query.order_by(Album.title.desc())
        else:
            query = query.order_by(Album.title.asc())
            
    # Execute query.
    #
    # `.unique()` prevents duplicate ORM objects when joins
    # produce repeated rows internally.
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

            # Convert Tag ORM objects into simple strings.
            tags=[
                tag.name
                for tag in item.tags
            ],

            # Convert Track ORM objects into API schemas.
            tracks=[
                TrackRead.model_validate(track)
                for track in item.album.tracks
            ],
        )
        for item in items
    ]