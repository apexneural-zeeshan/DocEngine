"""Security helpers for password hashing and JWT handling."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
from jose import jwt

from backend.src.core.config import load_settings


def _get_settings() -> tuple[str, str, int]:
    """Return secret key, algorithm, and token expiry in minutes."""
    settings = load_settings()
    return (
        settings.secret_key,
        settings.algorithm,
        settings.access_token_expire_minutes,
    )


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    if not isinstance(data, dict):
        raise ValueError("Token data must be a dict")

    secret_key, algorithm, expire_minutes = _get_settings()

    to_encode = dict(data)
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=expire_minutes)
    )
    to_encode["exp"] = expire

    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    if not token:
        raise ValueError("Token must be provided")

    secret_key, algorithm, _ = _get_settings()

    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    return dict(payload)
