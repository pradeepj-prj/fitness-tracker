from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, Index, UniqueConstraint, Text
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class FoodSource(str, Enum):
    OPEN_FOOD_FACTS = "open_food_facts"
    USDA = "usda"
    MANUAL = "manual"


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile = Column(String(50), nullable=False, default="vidhi", index=True)
    daily_calorie_goal = Column(Float, nullable=False, default=2000.0)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        UniqueConstraint("profile", name="uq_settings_profile"),
    )


class FoodEntry(Base):
    __tablename__ = "food_entries"

    id = Column(Integer, primary_key=True, index=True)
    profile = Column(String(50), nullable=False, default="vidhi", index=True)
    food_name = Column(String(255), nullable=False)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    source = Column(SQLEnum(FoodSource), default=FoodSource.MANUAL)
    logged_at = Column(DateTime, nullable=False, default=utcnow)
    created_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        Index("idx_food_entries_logged_at", "logged_at"),
        Index("idx_food_entries_profile_logged_at", "profile", "logged_at"),
    )


class WeightEntry(Base):
    __tablename__ = "weight_entries"

    id = Column(Integer, primary_key=True, index=True)
    profile = Column(String(50), nullable=False, default="vidhi", index=True)
    weight_kg = Column(Float, nullable=False)
    logged_at = Column(DateTime, nullable=False, default=utcnow)
    created_at = Column(DateTime, default=utcnow)
    note = Column(String(255), nullable=True)

    __table_args__ = (
        Index("idx_weight_entries_logged_at", "logged_at"),
        Index("idx_weight_entries_profile_logged_at", "profile", "logged_at"),
    )


class AgentConversation(Base):
    __tablename__ = "agent_conversations"

    id = Column(String(64), primary_key=True)
    profile = Column(String(50), nullable=False, default="vidhi", index=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("idx_agent_conversations_profile_updated_at", "profile", "updated_at"),
    )


class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(64), nullable=False, index=True)
    profile = Column(String(50), nullable=False, default="vidhi", index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tool_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    __table_args__ = (
        Index("idx_agent_messages_conversation_created_at", "conversation_id", "created_at"),
    )
