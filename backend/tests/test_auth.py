from fastapi import status

from backend.src.core.security import get_password_hash
from backend.src.models.user import User


def _create_user(session, *, email: str, password: str, is_active: bool = True) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        is_active=is_active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_login_success(client, db_session):
    email = "user@example.com"
    password = "P@ssw0rd!"
    _create_user(db_session, email=email, password=password)

    response = client.post("/auth/login", json={"email": email, "password": password})

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


def test_login_invalid_credentials(client, db_session):
    email = "user@example.com"
    _create_user(db_session, email=email, password="correct-password")

    response = client.post(
        "/auth/login",
        json={"email": email, "password": "wrong-password"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
