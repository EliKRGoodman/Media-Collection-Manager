from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.album import Album
from app.models.artist import Artist
from app.models.collection_item import CollectionItem
from app.schemas.collection_item import CollectionItemCreate, CollectionItemRead
from app.models.tag import Tag

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
    )


@router.get("/", response_model=list[CollectionItemRead])
def list_collection_items(db: Session = Depends(get_db)):
    items = db.scalars(select(CollectionItem)).all()

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
            tags=[tag.name for tag in item.tags],
        )
        for item in items
    ]