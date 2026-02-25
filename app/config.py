"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings from environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dashmessaging"

    # App
    DEBUG: bool = False
    SCHEDULER_POLL_INTERVAL_SECONDS: int = 1


settings = Settings()
