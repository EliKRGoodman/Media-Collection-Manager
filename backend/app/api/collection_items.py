from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.location import Location
from app.db.deps import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.models.collection_item import CollectionItem
from app.schemas.collection_item import CollectionItemCreate, CollectionItemRead
from app.models.tag import Tag
from app.models.track import Track
from app.schemas.collection_item import (
    CollectionItemCreate,
    CollectionItemRead,
    CollectionItemUpdate,
    TrackRead,
)

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
            image_url=item_in.image_url,
            artist_id=artist.id,
        )
        db.add(album)
        db.flush()

    # Reuse or create a Location when a location name is provided.
    #
    # CollectionItem now stores location_id, not a plain text location.
    # This keeps locations as real reusable domain objects.
    location = None

    if item_in.location_name:
        location = db.scalar(
            select(Location).where(Location.name == item_in.location_name)
        )

        if location is None:
            location = Location(name=item_in.location_name)
            db.add(location)
            db.flush()

    item = CollectionItem(
        album_id=album.id,
        condition=item_in.condition,
        notes=item_in.notes,
        location_id=location.id if location else None,
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
        image_url=item.album.image_url,
        condition=item.condition,
        notes=item.notes,
        location_name=item.location.name if item.location else None,
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

        # Maximum number of collection items to return.
    #
    # This prevents the API from returning the entire collection at once
    # once the database grows larger.
    limit: int = Query(default=25, ge=1, le=100),

    # Number of collection items to skip before returning results.
    #
    # Example:
    # offset=0 returns the first page
    # offset=25 returns the second page when limit=25
    offset: int = Query(default=0, ge=0),
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

    # Define allowed sorting fields for this endpoint.
    #
    # This prevents silent failures where the user provides an unsupported
    # sort field and the API quietly ignores it.
    allowed_sort_fields = {
        "artist",
        "album",
        "album_title",
        "release_year",
        "genre",
    }

    # Define allowed sort directions.
    allowed_sort_orders = {
        "asc",
        "desc",
    }

    # Validate sort_by if provided.
    if sort_by is not None and sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid sort_by value. "
                "Allowed values are: artist, album, album_title, release_year, genre."
            ),
        )

    # Normalize sort order before validation.
    sort_order = sort_order.lower()

    # Validate sort_order.
    if sort_order not in allowed_sort_orders:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_order value. Allowed values are: asc, desc.",
        )
    
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

    # Apply pagination after filtering/sorting.
    #
    # limit controls page size.
    # offset controls where the page starts.
    query = query.limit(limit).offset(offset)        
    
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
            image_url=item.album.image_url,
            condition=item.condition,
            notes=item.notes,
            location_name=item.location.name if item.location else None,
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

@router.patch("/{item_id}", response_model=CollectionItemRead)
def update_collection_item(
    item_id: int,
    item_in: CollectionItemUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing owned collection item.

    This edits collection-specific data only:
    - condition
    - notes
    - location
    - price
    - album rating
    - tags

    It intentionally does not edit album-level metadata such as:
    - album title
    - artist name
    - release year
    - genre

    Those should be handled by separate album/metadata endpoints later.
    """

    # Find the collection item by primary key.
    item = db.get(CollectionItem, item_id)

    # If no item exists with that id, return a clear 404 response.
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Collection item not found.",
        )

    # Convert the incoming Pydantic model to a dictionary,
    # excluding fields the caller did not provide.
    update_data = item_in.model_dump(exclude_unset=True)

    # Update simple scalar fields if they were provided.
    for field in [
        "condition",
        "notes",
        "price",
        "album_rating",
    ]:
        if field in update_data:
            setattr(item, field, update_data[field])

    # If tags was provided, replace the item's tag list.
    #
    # This makes the update behavior simple and predictable:
    # the submitted list becomes the complete current tag set.
    if "tags" in update_data:
        tag_names = {
            tag.strip()
            for tag in update_data["tags"]
            if tag.strip()
        }

        new_tags = []

        for tag_name in tag_names:
            tag = db.scalar(
                select(Tag).where(Tag.name == tag_name)
            )

            if tag is None:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()

            new_tags.append(tag)

        item.tags = new_tags

    # If location_name was provided, update the item's Location.
    #
    # - If location_name is a real string, reuse/create that Location.
    # - If location_name is None, clear the location.
    if "location_name" in update_data:

        location_name = update_data["location_name"]

        # Clear location if explicitly set to null.
        if location_name is None:
            item.location_id = None

        else:
            # Try to reuse an existing Location first.
            location = db.scalar(
                select(Location).where(
                    Location.name == location_name
                )
            )

            # Create Location if it does not exist yet.
            if location is None:
                location = Location(name=location_name)

                db.add(location)
                db.flush()

            # Attach collection item to the Location.
            item.location_id = location.id

    db.commit()
    db.refresh(item)

    return CollectionItemRead(
        id=item.id,
        artist_name=item.album.artist.name,
        album_title=item.album.title,
        release_year=item.album.release_year,
        genre=item.album.genre,
        image_url=item.album.image_url,
        condition=item.condition,
        notes=item.notes,
        location_name=item.location.name if item.location else None,
        price=item.price,
        album_rating=item.album_rating,
        date_added=item.date_added,
        tags=[
            tag.name
            for tag in item.tags
        ],
        tracks=[
            TrackRead.model_validate(track)
            for track in item.album.tracks
        ],
    )

@router.delete("/{item_id}")
def delete_collection_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete an owned collection item.

    V1 behavior:
    - This performs a hard delete.
    - The CollectionItem row is removed from the database.

    Important:
    - This does NOT delete the related Album or Artist.
    - That is intentional because another owned copy may still reference
      the same album metadata.
    - Later, we may replace this with a soft-delete/archive workflow.
    """

    # Look up the owned collection item by primary key.
    item = db.get(CollectionItem, item_id)

    # Return a clear 404 error if the item does not exist.
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Collection item not found.",
        )

    # Delete only the owned copy.
    # Related album/artist metadata remains intact.
    db.delete(item)
    db.commit()

    return {
        "message": "Collection item deleted.",
        "collection_item_id": item_id,
    }