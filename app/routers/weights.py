from datetime import datetime, date, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import WeightEntry
from app.schemas import WeightEntryCreate, WeightEntryUpdate, WeightEntryResponse

router = APIRouter(prefix="/weights", tags=["Weight Entries"])


@router.post("", response_model=WeightEntryResponse, status_code=201)
def create_weight_entry(data: WeightEntryCreate, db: Session = Depends(get_db)):
    entry = WeightEntry(
        profile=data.profile or "vidhi",
        weight_kg=data.weight_kg,
        logged_at=data.logged_at or datetime.now(timezone.utc),
        note=data.note,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=List[WeightEntryResponse])
def list_weight_entries(
    profile: str = Query("vidhi", min_length=1, max_length=50),
    date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(WeightEntry).filter(WeightEntry.profile == profile)
    if date:
        query = query.filter(func.date(WeightEntry.logged_at) == date)
    query = query.order_by(WeightEntry.logged_at.desc())
    return query.offset(offset).limit(limit).all()


@router.get("/latest", response_model=WeightEntryResponse)
def get_latest_weight_entry(
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    entry = db.query(WeightEntry).filter(WeightEntry.profile == profile).order_by(WeightEntry.logged_at.desc()).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Weight entry not found")
    return entry


@router.get("/{entry_id}", response_model=WeightEntryResponse)
def get_weight_entry(
    entry_id: int,
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    entry = db.query(WeightEntry).filter(WeightEntry.id == entry_id, WeightEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Weight entry not found")
    return entry


@router.put("/{entry_id}", response_model=WeightEntryResponse)
def update_weight_entry(
    entry_id: int,
    data: WeightEntryUpdate,
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    entry = db.query(WeightEntry).filter(WeightEntry.id == entry_id, WeightEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Weight entry not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_weight_entry(
    entry_id: int,
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    entry = db.query(WeightEntry).filter(WeightEntry.id == entry_id, WeightEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Weight entry not found")
    db.delete(entry)
    db.commit()
