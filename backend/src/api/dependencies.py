import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.core.security import decode_access_token
from backend.src.db.session import get_session
from backend.src.models.user import User

_bearer_scheme = HTTPBearer(auto_error=False)


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    session: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _credentials_exception()

    try:
        payload = decode_access_token(credentials.credentials)
    except (JWTError, ValueError):
        raise _credentials_exception()

    subject = payload.get("sub")
    if not subject:
        raise _credentials_exception()

    try:
        user_id = uuid.UUID(str(subject))
    except ValueError:
        raise _credentials_exception()

    statement = select(User).where(User.id == user_id)
    user = session.scalars(statement).first()
    if user is None or not user.is_active:
        raise _credentials_exception()

    return user
