import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.src.models.base import Base
from backend.src.models import approval_step, audit_log, document, user  # noqa: F401

DATABASE_URL = os.getenv("DOCENGINE_DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DOCENGINE_DATABASE_URL is not set.")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
)
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
