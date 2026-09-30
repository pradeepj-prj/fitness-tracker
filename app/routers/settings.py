from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Settings
from app.schemas import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SettingsResponse)
def get_settings(
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    settings = db.query(Settings).filter(Settings.profile == profile).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings profile not found")
    return settings


@router.put("", response_model=SettingsResponse)
def update_settings(
    data: SettingsUpdate,
    profile: str = Query("vidhi", min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    settings = db.query(Settings).filter(Settings.profile == profile).first()
    if not settings:
        settings = Settings(profile=profile, daily_calorie_goal=data.daily_calorie_goal)
        db.add(settings)
    else:
        settings.daily_calorie_goal = data.daily_calorie_goal
    db.commit()
    db.refresh(settings)
    return settings
