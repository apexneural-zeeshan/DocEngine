import uuid

from fastapi import status

from backend.src.core.security import create_access_token, get_password_hash
from backend.src.models.approval_step import ApprovalStep, ApprovalStepStatus
from backend.src.models.document import Document, DocumentStatus
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


def _create_document(session, *, title: str) -> Document:
    document = Document(title=title, status=DocumentStatus.PENDING)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def _create_step(
    session,
    *,
    document_id: uuid.UUID,
    approver_id: uuid.UUID,
    step_order: int,
    status: ApprovalStepStatus = ApprovalStepStatus.PENDING,
) -> ApprovalStep:
    step = ApprovalStep(
        document_id=document_id,
        approver_id=approver_id,
        step_order=step_order,
        status=status,
    )
    session.add(step)
    session.commit()
    session.refresh(step)
    return step


def test_approve_invalid_step_order(client, db_session):
    api_user = _create_user(db_session, email="api@example.com", password="P@ssw0rd!")
    document = _create_document(db_session, title="Policy Draft")
    approver_id = uuid.uuid4()
    step1 = _create_step(
        db_session,
        document_id=document.id,
        approver_id=approver_id,
        step_order=1,
    )
    step2 = _create_step(
        db_session,
        document_id=document.id,
        approver_id=approver_id,
        step_order=2,
    )

    response = client.post(
        f"/documents/{document.id}/steps/{step2.id}/approve",
        json={"approver_id": str(approver_id)},
        headers=_auth_headers_for(api_user),
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_approve_unauthorized_approver(client, db_session):
    api_user = _create_user(db_session, email="api@example.com", password="P@ssw0rd!")
    document = _create_document(db_session, title="Policy Draft")
    step = _create_step(
        db_session,
        document_id=document.id,
        approver_id=uuid.uuid4(),
        step_order=1,
    )

    response = client.post(
        f"/documents/{document.id}/steps/{step.id}/approve",
        json={"approver_id": str(uuid.uuid4())},
        headers=_auth_headers_for(api_user),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_successful_approval_updates_document_status(client, db_session):
    api_user = _create_user(db_session, email="api@example.com", password="P@ssw0rd!")
    document = _create_document(db_session, title="Policy Draft")
    approver_id = uuid.uuid4()
    step1 = _create_step(
        db_session,
        document_id=document.id,
        approver_id=approver_id,
        step_order=1,
    )
    step2 = _create_step(
        db_session,
        document_id=document.id,
        approver_id=approver_id,
        step_order=2,
    )

    response_step1 = client.post(
        f"/documents/{document.id}/steps/{step1.id}/approve",
        json={"approver_id": str(approver_id)},
        headers=_auth_headers_for(api_user),
    )

    assert response_step1.status_code == status.HTTP_200_OK
    payload_step1 = response_step1.json()
    assert payload_step1["step"]["status"] == ApprovalStepStatus.APPROVED.value
    assert payload_step1["document"]["status"] == DocumentStatus.PENDING.value

    response_step2 = client.post(
        f"/documents/{document.id}/steps/{step2.id}/approve",
        json={"approver_id": str(approver_id)},
        headers=_auth_headers_for(api_user),
    )

    assert response_step2.status_code == status.HTTP_200_OK
    payload_step2 = response_step2.json()
    assert payload_step2["step"]["status"] == ApprovalStepStatus.APPROVED.value
    assert payload_step2["document"]["status"] == DocumentStatus.APPROVED.value
