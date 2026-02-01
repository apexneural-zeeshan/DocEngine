"""Application configuration loading."""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
_ENV_PREFIX = "DOCENGINE_"


class Settings(BaseSettings):
    """Typed application settings."""

    app_name: str = Field(
        default="DocEngine",
        validation_alias=AliasChoices(
            "DOCENGINE_APP_NAME",
            "docengine_app_name",
        ),
    )
    environment: str = Field(
        validation_alias=AliasChoices(
            "DOCENGINE_ENVIRONMENT",
            "docengine_environment",
        ),
    )
    database_url: str = Field(
        validation_alias=AliasChoices(
            "DOCENGINE_DATABASE_URL",
            "docengine_database_url",
        ),
    )
    secret_key: str = Field(
        default="change-me",
        validation_alias=AliasChoices(
            "DOCENGINE_SECRET_KEY",
            "docengine_secret_key",
        ),
    )
    algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices(
            "DOCENGINE_ALGORITHM",
            "docengine_algorithm",
        ),
    )
    access_token_expire_minutes: int = Field(
        default=60,
        validation_alias=AliasChoices(
            "DOCENGINE_ACCESS_TOKEN_EXPIRE_MINUTES",
            "docengine_access_token_expire_minutes",
        ),
    )

    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH),
        extra="forbid",
        case_sensitive=True,
    )


def validate_settings() -> Settings:
    """Environment-aware configuration validation."""
    try:
        settings = Settings()
    except ValidationError as exc:
        missing: list[str] = []
        invalid: list[str] = []
        for err in exc.errors():
            loc = err.get("loc") or ()
            field = str(loc[0]) if loc else "unknown"
            env_name = f"{_ENV_PREFIX}{field.upper()}"
            if err.get("type") == "missing":
                if env_name not in missing:
                    missing.append(env_name)
                continue
            detail = err.get("msg", "invalid")
            entry = f"{env_name} ({detail})"
            if entry not in invalid:
                invalid.append(entry)

        parts: list[str] = []
        if missing:
            parts.append(f"Missing: {', '.join(missing)}")
        if invalid:
            parts.append(f"Invalid: {', '.join(invalid)}")
        detail = "; ".join(parts) if parts else "Invalid configuration."
        raise RuntimeError(f"Configuration error. {detail}") from exc

    env = settings.environment.strip().lower()
    if env not in {"production", "development", "test"}:
        raise RuntimeError(
            "Configuration error. Invalid: DOCENGINE_ENVIRONMENT "
            "(must be production, development, or test)"
        )

    required_by_env: dict[str, set[str]] = {
        "production": {"environment", "database_url", "secret_key", "algorithm", "access_token_expire_minutes", "app_name"},
        "development": {"environment", "database_url", "secret_key", "algorithm", "access_token_expire_minutes", "app_name"},
        "test": {"environment", "database_url"},
    }
    required_fields = required_by_env[env]

    missing_required = [
        f"{_ENV_PREFIX}{field.upper()}"
        for field in required_fields
        if field not in settings.model_fields_set
        or (
            isinstance(getattr(settings, field), str)
            and not getattr(settings, field).strip()
        )
    ]
    if missing_required:
        raise RuntimeError(
            f"Configuration error. Missing: {', '.join(missing_required)}"
        )

    return settings


@lru_cache
def load_settings() -> Settings:
    """Load and cache validated settings."""
    return validate_settings()
