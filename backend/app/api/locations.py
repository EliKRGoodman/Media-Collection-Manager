"""
Location API routes.

Locations represent real organizational structures such as:
- shelves,
- boxes,
- storage units,
etc.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.location import Location
from app.schemas.location import (
    LocationCreate,
    LocationRead,
)

router = APIRouter(
    prefix="/locations",
    tags=["locations"],
)


@router.post("/", response_model=LocationRead)
def create_location(
    location_in: LocationCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new location.

    Location names must be unique.
    """

    # Prevent duplicate location names.
    existing_location = db.scalar(
        select(Location).where(
            Location.name == location_in.name
        )
    )

    if existing_location is not None:
        raise HTTPException(
            status_code=400,
            detail="Location already exists.",
        )

    location = Location(
        name=location_in.name,
        capacity=location_in.capacity,
    )

    db.add(location)
    db.commit()
    db.refresh(location)

    return location


@router.get("/", response_model=list[LocationRead])
def list_locations(
    db: Session = Depends(get_db),
):
    """
    Return all locations.
    """

    locations = db.scalars(
        select(Location).order_by(Location.name.asc())
    ).all()

    return locations