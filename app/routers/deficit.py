from datetime import date as date_type, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import FoodEntry, Settings
from app.schemas import DeficitResponse

router = APIRouter(prefix="/deficit", tags=["Deficit"])


def calculate_deficit(db: Session, profile: str, target_date: date_type) -> DeficitResponse:
    settings = db.query(Settings).filter(Settings.profile == profile).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings profile not found")

    daily_goal = settings.daily_calorie_goal

    result = db.query(
        func.coalesce(func.sum(FoodEntry.calories), 0).label("total"),
        func.count(FoodEntry.id).label("count"),
    ).filter(
        FoodEntry.profile == profile,
        func.date(FoodEntry.logged_at) == target_date,
    ).first()

    total_consumed = float(result.total)
    entries_count = result.count

    return DeficitResponse(
        date=target_date,
        profile=profile,
        daily_goal=daily_goal,
        total_consumed=total_consumed,
        remaining=daily_goal - total_consumed,
        entries_count=entries_count,
    )


@router.get("/today", response_model=DeficitResponse)
def get_deficit_today(
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    return calculate_deficit(db, profile, datetime.now(timezone.utc).date())


@router.get("/{date}", response_model=DeficitResponse)
def get_deficit_by_date(
    date: date_type,
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    return calculate_deficit(db, profile, date)
