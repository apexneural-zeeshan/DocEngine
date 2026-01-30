"""Application configuration loading."""

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"

# Load .env early so settings are available during module imports (e.g., DB setup).
load_dotenv(dotenv_path=_ENV_PATH, override=False)


class Settings(BaseSettings):
    """Typed settings loaded from environment or .env."""

    app_name: str
    environment: str
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_prefix="DOCENGINE_",
        env_file=str(_ENV_PATH),
    )


@lru_cache
def load_settings() -> Settings:
    """Load and cache application settings."""
    return Settings()
