from __future__ import annotations

from datetime import date as date_type, datetime, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import FoodEntry, FoodSource, Settings, WeightEntry
from app.routers.deficit import calculate_deficit


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_date(value: str | None) -> date_type:
    if not value:
        return datetime.now(timezone.utc).date()
    return date_type.fromisoformat(value)


def _food_entry_payload(entry: FoodEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "profile": entry.profile,
        "food_name": entry.food_name,
        "calories": entry.calories,
        "protein_g": entry.protein_g,
        "carbs_g": entry.carbs_g,
        "fat_g": entry.fat_g,
        "source": entry.source.value if entry.source else None,
        "logged_at": entry.logged_at.isoformat(),
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


def _weight_entry_payload(entry: WeightEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "profile": entry.profile,
        "weight_kg": entry.weight_kg,
        "logged_at": entry.logged_at.isoformat(),
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "note": entry.note,
    }


def get_settings(db: Session, profile: str = "vidhi") -> dict[str, Any]:
    row = db.query(Settings).filter(Settings.profile == profile).first()
    if not row:
        raise HTTPException(status_code=404, detail="Settings profile not found")
    return {
        "id": row.id,
        "profile": row.profile,
        "daily_calorie_goal": row.daily_calorie_goal,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def update_settings(db: Session, profile: str = "vidhi", daily_calorie_goal: float = 1500) -> dict[str, Any]:
    row = db.query(Settings).filter(Settings.profile == profile).first()
    if not row:
        row = Settings(profile=profile, daily_calorie_goal=daily_calorie_goal)
        db.add(row)
    else:
        row.daily_calorie_goal = daily_calorie_goal
    db.commit()
    db.refresh(row)
    return get_settings(db, profile)


def list_entries(db: Session, profile: str = "vidhi", date: str | None = None, limit: int = 25) -> list[dict[str, Any]]:
    query = db.query(FoodEntry).filter(FoodEntry.profile == profile)
    if date:
        query = query.filter(func.date(FoodEntry.logged_at) == _parse_date(date))
    rows = query.order_by(FoodEntry.logged_at.desc()).limit(min(limit, 100)).all()
    return [_food_entry_payload(row) for row in rows]


def create_food_entry(
    db: Session,
    profile: str = "vidhi",
    food_name: str = "",
    calories: float = 0,
    protein_g: float | None = None,
    carbs_g: float | None = None,
    fat_g: float | None = None,
    logged_at: str | None = None,
) -> dict[str, Any]:
    entry = FoodEntry(
        profile=profile,
        food_name=food_name,
        calories=calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        source=FoodSource.MANUAL,
        logged_at=_parse_datetime(logged_at),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _food_entry_payload(entry)


def update_food_entry(db: Session, profile: str = "vidhi", entry_id: int = 0, **changes: Any) -> dict[str, Any]:
    entry = db.query(FoodEntry).filter(FoodEntry.id == entry_id, FoodEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")

    allowed = {"food_name", "calories", "protein_g", "carbs_g", "fat_g", "logged_at"}
    for key, value in changes.items():
        if key not in allowed or value is None:
            continue
        if key == "logged_at":
            value = _parse_datetime(value)
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return _food_entry_payload(entry)


def delete_food_entry(db: Session, profile: str = "vidhi", entry_id: int = 0) -> dict[str, Any]:
    entry = db.query(FoodEntry).filter(FoodEntry.id == entry_id, FoodEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Food entry not found")
    payload = _food_entry_payload(entry)
    db.delete(entry)
    db.commit()
    return {"deleted": True, "entry": payload}


def get_deficit(db: Session, profile: str = "vidhi", date: str | None = None) -> dict[str, Any]:
    target_date = _parse_date(date)
    deficit = calculate_deficit(db, profile, target_date)
    return deficit.model_dump(mode="json")


def list_weights(db: Session, profile: str = "vidhi", limit: int = 25) -> list[dict[str, Any]]:
    rows = (
        db.query(WeightEntry)
        .filter(WeightEntry.profile == profile)
        .order_by(WeightEntry.logged_at.desc())
        .limit(min(limit, 100))
        .all()
    )
    return [_weight_entry_payload(row) for row in rows]


def create_weight_entry(
    db: Session,
    profile: str = "vidhi",
    weight_kg: float = 0,
    logged_at: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    entry = WeightEntry(
        profile=profile,
        weight_kg=weight_kg,
        logged_at=_parse_datetime(logged_at),
        note=note,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _weight_entry_payload(entry)


def update_weight_entry(db: Session, profile: str = "vidhi", entry_id: int = 0, **changes: Any) -> dict[str, Any]:
    entry = db.query(WeightEntry).filter(WeightEntry.id == entry_id, WeightEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Weight entry not found")

    allowed = {"weight_kg", "logged_at", "note"}
    for key, value in changes.items():
        if key not in allowed or value is None:
            continue
        if key == "logged_at":
            value = _parse_datetime(value)
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return _weight_entry_payload(entry)


def delete_weight_entry(db: Session, profile: str = "vidhi", entry_id: int = 0) -> dict[str, Any]:
    entry = db.query(WeightEntry).filter(WeightEntry.id == entry_id, WeightEntry.profile == profile).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Weight entry not found")
    payload = _weight_entry_payload(entry)
    db.delete(entry)
    db.commit()
    return {"deleted": True, "entry": payload}


TOOL_FUNCTIONS = {
    "get_settings": get_settings,
    "update_settings": update_settings,
    "list_entries": list_entries,
    "create_food_entry": create_food_entry,
    "update_food_entry": update_food_entry,
    "delete_food_entry": delete_food_entry,
    "get_deficit": get_deficit,
    "list_weights": list_weights,
    "create_weight_entry": create_weight_entry,
    "update_weight_entry": update_weight_entry,
    "delete_weight_entry": delete_weight_entry,
}


TOOL_SCHEMAS = [
    {
        "type": "function",
        "name": "get_settings",
        "description": "Read the daily calorie goal for a profile.",
        "parameters": {
            "type": "object",
            "properties": {"profile": {"type": "string", "default": "vidhi"}},
            "required": ["profile"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "update_settings",
        "description": "Update the daily calorie goal for a profile.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "default": "vidhi"},
                "daily_calorie_goal": {"type": "number", "minimum": 1},
            },
            "required": ["profile", "daily_calorie_goal"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_entries",
        "description": "List food entries, optionally for a YYYY-MM-DD date.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "default": "vidhi"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 25},
            },
            "required": ["profile"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "create_food_entry",
        "description": "Create a manually estimated food entry.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "default": "vidhi"},
                "food_name": {"type": "string"},
                "calories": {"type": "number", "minimum": 0},
                "protein_g": {"type": ["number", "null"], "minimum": 0},
                "carbs_g": {"type": ["number", "null"], "minimum": 0},
                "fat_g": {"type": ["number", "null"], "minimum": 0},
                "logged_at": {"type": ["string", "null"], "description": "ISO timestamp; omit for now."},
            },
            "required": ["profile", "food_name", "calories"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "update_food_entry",
        "description": "Correct a food entry by id.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "default": "vidhi"},
                "entry_id": {"type": "integer"},
                "food_name": {"type": ["string", "null"]},
                "calories": {"type": ["number", "null"], "minimum": 0},
                "protein_g": {"type": ["number", "null"], "minimum": 0},
                "carbs_g": {"type": ["number", "null"], "minimum": 0},
                "fat_g": {"type": ["number", "null"], "minimum": 0},
                "logged_at": {"type": ["string", "null"]},
            },
            "required": ["profile", "entry_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "delete_food_entry",
        "description": "Delete a food entry by id.",
        "parameters": {
            "type": "object",
            "properties": {"profile": {"type": "string"}, "entry_id": {"type": "integer"}},
            "required": ["profile", "entry_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_deficit",
        "description": "Get goal, consumed calories, remaining calories, and entry count.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "default": "vidhi"},
                "date": {"type": ["string", "null"], "description": "YYYY-MM-DD; omit for today."},
            },
            "required": ["profile"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "list_weights",
        "description": "List recent weigh-ins for a profile.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "default": "vidhi"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 25},
            },
            "required": ["profile"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "create_weight_entry",
        "description": "Create a weigh-in entry. Use directly when a user reports a weight.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "default": "vidhi"},
                "weight_kg": {"type": "number", "minimum": 1},
                "logged_at": {"type": ["string", "null"]},
                "note": {"type": ["string", "null"]},
            },
            "required": ["profile", "weight_kg"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "update_weight_entry",
        "description": "Correct a weigh-in entry by id.",
        "parameters": {
            "type": "object",
            "properties": {
                "profile": {"type": "string", "default": "vidhi"},
                "entry_id": {"type": "integer"},
                "weight_kg": {"type": ["number", "null"], "minimum": 1},
                "logged_at": {"type": ["string", "null"]},
                "note": {"type": ["string", "null"]},
            },
            "required": ["profile", "entry_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "delete_weight_entry",
        "description": "Delete a weigh-in entry by id.",
        "parameters": {
            "type": "object",
            "properties": {"profile": {"type": "string"}, "entry_id": {"type": "integer"}},
            "required": ["profile", "entry_id"],
            "additionalProperties": False,
        },
    },
]
