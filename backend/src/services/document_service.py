import uuid

from sqlalchemy.orm import Session

from backend.src.models.document import Document


def create_document(session: Session, *, title: str) -> Document:
    document = Document(title=title)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def get_document(session: Session, *, document_id: uuid.UUID) -> Document | None:
    return session.get(Document, document_id)
