from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_PATH: str = "calorie_tracker.db"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-5-mini"
    AUTH_USERNAME: str = "tracker"
    AUTH_PASSWORD: Optional[str] = None
    SESSION_SECRET: Optional[str] = None
    SESSION_DAYS: int = 30
    SESSION_COOKIE_SECURE: bool = True
    AGENT_CONTEXT_MESSAGE_LIMIT: int = 24
    AGENT_TRANSCRIPT_RETENTION_LIMIT: int = 200
    USDA_API_KEY: Optional[str] = None


settings = Settings()
