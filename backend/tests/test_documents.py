from fastapi import status

from backend.src.core.security import create_access_token, get_password_hash
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


def _auth_headers_for(user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"Authorization": f"Bearer {token}"}


def test_create_document_requires_auth(client):
    response = client.post("/documents", json={"title": "Quarterly Report"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    payload = response.json()
    assert payload["detail"] == "Could not validate credentials."


def test_create_document_success(client, db_session):
    user = _create_user(db_session, email="author@example.com", password="P@ssw0rd!")

    response = client.post(
        "/documents",
        json={"title": "Quarterly Report"},
        headers=_auth_headers_for(user),
    )

    assert response.status_code == status.HTTP_201_CREATED
    payload = response.json()
    assert payload["title"] == "Quarterly Report"
    assert payload["id"]
    assert payload["status"]


def test_create_document_validation_error(client, db_session):
    user = _create_user(db_session, email="author@example.com", password="P@ssw0rd!")

    response = client.post(
        "/documents",
        json={"title": ""},
        headers=_auth_headers_for(user),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
