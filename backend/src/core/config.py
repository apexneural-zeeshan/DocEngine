from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DocEngine"
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_prefix="DOCENGINE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def load_settings() -> Settings:
    return Settings()
