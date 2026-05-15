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

    collection_items = relationship(
        "CollectionItem",
        back_populates="album",
    )