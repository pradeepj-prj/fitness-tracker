from datetime import datetime, date, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import FoodEntry
from app.schemas import FoodEntryCreate, FoodEntryUpdate, FoodEntryResponse

router = APIRouter(prefix="/entries", tags=["Food Entries"])


@router.post("", response_model=FoodEntryResponse, status_code=201)
def create_entry(data: FoodEntryCreate, db: Session = Depends(get_db)):
    entry = FoodEntry(
        profile=data.profile or "vidhi",
        food_name=data.food_name,
        calories=data.calories,
        protein_g=data.protein_g,
        carbs_g=data.carbs_g,
        fat_g=data.fat_g,
        source=data.source,
        logged_at=data.logged_at or datetime.now(timezone.utc),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=List[FoodEntryResponse])
def list_entries(
    profile: str = Query("vidhi", min_length=1, max_length=50),
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(FoodEntry).filter(FoodEntry.profile == profile)
    if date:
        query = query.filter(func.date(FoodEntry.logged_at) == date)
    query = query.order_by(FoodEntry.logged_at.desc())
    return query.offset(offset).limit(limit).all()


@router.get("/{entry_id}", response_model=FoodEntryResponse)
def get_entry(
    entry_id: int,
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    entry = db.query(FoodEntry).filter(FoodEntry.id == entry_id, FoodEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")
    return entry


@router.put("/{entry_id}", response_model=FoodEntryResponse)
def update_entry(
    entry_id: int,
    data: FoodEntryUpdate,
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    entry = db.query(FoodEntry).filter(FoodEntry.id == entry_id, FoodEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(
    entry_id: int,
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    entry = db.query(FoodEntry).filter(FoodEntry.id == entry_id, FoodEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")
    db.delete(entry)
    db.commit()
