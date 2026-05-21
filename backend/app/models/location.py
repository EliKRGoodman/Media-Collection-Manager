"""
Location model.

Represents a real organizational structure in the collection,
such as:
- shelf,
- box,
- cabinet,
- storage crate,
etc.

This replaces the earlier simple string location field.
"""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Location(Base):
    """
    Represents a physical organizational location.
    """

    __tablename__ = "locations"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Human-readable location name.
    #
    # Examples:
    # - Shelf A
    # - Vinyl Box 1
    # - Listening Room
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # Optional capacity limit.
    #
    # Future use:
    # warn/prevent adding items when full.
    capacity: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # One location can contain many collection items.
    collection_items = relationship(
        "CollectionItem",
        back_populates="location",
    )