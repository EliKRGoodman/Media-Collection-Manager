from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.collection_item_tag import collection_item_tags
from app.db.base import Base


class CollectionItem(Base):
    __tablename__ = "collection_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    album_id: Mapped[int] = mapped_column(
        ForeignKey("albums.id"),
        nullable=False,
    )

    condition: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # Foreign key linking this owned item to a Location.
    #
    # Nullable for now because V1 allows incomplete data.
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True,
    )

    price: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    album_rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    date_added: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    album = relationship(
        "Album",
        back_populates="collection_items",
    )

    tags = relationship(
        "Tag",
        secondary=collection_item_tags,
        back_populates="collection_items",
    )

        # ORM relationship to Location.
    #
    # Allows:
    # item.location
    location = relationship(
        "Location",
        back_populates="collection_items",
    )