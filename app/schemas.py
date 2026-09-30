from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models import FoodSource


# Settings schemas
class SettingsUpdate(BaseModel):
    daily_calorie_goal: float = Field(..., gt=0, le=10000)


class SettingsResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    profile: str
    daily_calorie_goal: float
    created_at: datetime
    updated_at: datetime


# Food entry schemas
class FoodEntryCreate(BaseModel):
    profile: Optional[str] = Field(None, min_length=1, max_length=50)
    food_name: str = Field(..., min_length=1, max_length=255)
    calories: float = Field(..., ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    source: FoodSource = FoodSource.MANUAL
    logged_at: Optional[datetime] = None


class FoodEntryUpdate(BaseModel):
    profile: Optional[str] = Field(None, min_length=1, max_length=50)
    food_name: Optional[str] = Field(None, min_length=1, max_length=255)
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    logged_at: Optional[datetime] = None


class FoodEntryResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    profile: str
    food_name: str
    calories: float
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    source: FoodSource
    logged_at: datetime
    created_at: datetime


# Weight entry schemas
class WeightEntryCreate(BaseModel):
    profile: Optional[str] = Field(None, min_length=1, max_length=50)
    weight_kg: float = Field(..., gt=0, le=500)
    logged_at: Optional[datetime] = None
    note: Optional[str] = Field(None, max_length=255)


class WeightEntryUpdate(BaseModel):
    profile: Optional[str] = Field(None, min_length=1, max_length=50)
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    logged_at: Optional[datetime] = None
    note: Optional[str] = Field(None, max_length=255)


class WeightEntryResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    profile: str
    weight_kg: float
    logged_at: datetime
    created_at: datetime
    note: Optional[str]


# Deficit schemas
class DeficitResponse(BaseModel):
    date: date
    profile: str
    daily_goal: float
    total_consumed: float
    remaining: float
    entries_count: int


# Food search schemas
class FoodItem(BaseModel):
    name: str
    calories: float
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    source: FoodSource


class FoodSearchResponse(BaseModel):
    query: str
    results: List[FoodItem]
    total_results: int


# Agent chat schemas
class AgentMessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime


class AgentChatResponse(BaseModel):
    conversation_id: str
    profile: str
    reply: str
    messages: List[AgentMessageResponse]
