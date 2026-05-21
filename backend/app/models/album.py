from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    release_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    genre: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id"),
        nullable=False,
    )

    artist = relationship(
        "Artist",
        back_populates="albums",
    )

        # Primary image URL for the album.
    #
    # V1 simplification:
    # We store only one image URL directly on Album.
    #
    # Later this can evolve into:
    # - separate Image entity
    # - multiple images
    # - image types (front/back/inside)
    # - local caching/storage
    image_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # External metadata source identifiers.
    #
    # These let us reconnect local albums to external APIs later.
    #
    # Example future uses:
    # - refresh metadata
    # - fetch updated images
    # - open Discogs page
    # - sync Spotify/Wikipedia data

    musicbrainz_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )

    discogs_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )

    collection_items = relationship(
        "CollectionItem",
        back_populates="album",
    )

        # One-to-many relationship:
    # one album can contain many tracks.
    #
    # Example:
    # Album: OK Computer
    # Tracks:
    #   Airbag
    #   Paranoid Android
    #   Subterranean Homesick Alien
    tracks = relationship(
        "Track",
        back_populates="album",
    )

    