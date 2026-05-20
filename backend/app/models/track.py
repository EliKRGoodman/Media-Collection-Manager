# SQLAlchemy column/data types
from sqlalchemy import ForeignKey, Integer, String

# ORM typing + relationship helpers
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Shared declarative base class
from app.db.base import Base


class Track(Base):
    """
    Represents an individual song/track belonging to an album.

    This exists as its own entity because:
    - tracks need to be searchable,
    - tracks can have ratings,
    - track metadata may later be imported from external APIs,
    - and tracks are conceptually distinct from albums.
    """

    __tablename__ = "tracks"

    # Primary key for the track row
    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign key linking this track to its parent album.
    # Every track must belong to an album.
    album_id: Mapped[int] = mapped_column(
        ForeignKey("albums.id"),
        nullable=False,
    )

    # Track title/song name
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Position of the track on the album.
    # Example:
    # 1 = first song
    # 2 = second song
    track_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Runtime in seconds.
    # Stored as integer for easier sorting/filtering/calculations.
    #
    # Example:
    # 245 = 4 minutes 5 seconds
    runtime_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Optional user rating for the song.
    #
    # V1 design decision:
    # Ratings are currently treated as single-user data,
    # so storing them directly on Track is acceptable.
    #
    # If the system later becomes multi-user,
    # ratings would likely move to a separate user-rating table.
    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ORM relationship back to Album.
    #
    # This allows:
    # track.album
    #
    # and creates the inverse side of:
    # album.tracks
    album = relationship(
        "Album",
        back_populates="tracks",
    )