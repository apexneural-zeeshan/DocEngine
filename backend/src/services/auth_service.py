"""Authentication domain logic and JWT issuance."""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.src.core.security import create_access_token, verify_password
from backend.src.models.user import User


class AuthenticationError(RuntimeError):
    """Base class for authentication failures."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when an email/password combination is invalid."""


class UserNotFoundError(AuthenticationError):
    """Raised when no user exists for the provided email."""


class InactiveUserError(AuthenticationError):
    """Raised when the user account is inactive."""


class AuthenticationInputError(AuthenticationError):
    """Raised when authentication inputs are invalid."""


@dataclass(frozen=True)
class AuthResult:
    """Authentication result including the access token."""
    user: User
    access_token: str
    token_type: str = "bearer"


def authenticate_user(
    session: Session,
    *,
    email: str,
    password: str,
    expires_delta: timedelta | None = None,
) -> AuthResult:
    """Authenticate credentials and return an access token."""
    normalized_email = _normalize_email(email)
    user = _load_user_by_email(session, normalized_email)

    if not user.is_active:
        raise InactiveUserError(f"User {user.email} is inactive.")
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError("Invalid email or password.")

    token_payload = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(token_payload, expires_delta=expires_delta)
    return AuthResult(user=user, access_token=access_token)


def _normalize_email(email: str) -> str:
    if not isinstance(email, str):
        raise AuthenticationInputError("Email must be a string.")
    normalized = email.strip().lower()
    if not normalized:
        raise AuthenticationInputError("Email must be provided.")
    return normalized


def _load_user_by_email(session: Session, email: str) -> User:
    statement = select(User).where(func.lower(User.email) == email)
    user = session.scalars(statement).first()
    if user is None:
        raise UserNotFoundError(f"No user found for email {email}.")
    return user
