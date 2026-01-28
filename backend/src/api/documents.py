import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.src.api.dependencies import get_current_user
from backend.src.db.session import get_session
from backend.src.models.document import DocumentStatus
from backend.src.models.user import User
from backend.src.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    status: DocumentStatus
    created_at: datetime


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    payload: DocumentCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    document = document_service.create_document(session, title=payload.title)
    return document


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    document = document_service.get_document(session, document_id=document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document
