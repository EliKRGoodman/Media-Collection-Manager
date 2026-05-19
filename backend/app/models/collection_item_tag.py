from sqlalchemy import Column, ForeignKey, Table

from app.db.base import Base


collection_item_tags = Table(
    "collection_item_tags",
    Base.metadata,
    Column(
        "collection_item_id",
        ForeignKey("collection_items.id"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id"),
        primary_key=True,
    ),
)