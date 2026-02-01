"""Database session configuration and dependency helpers."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.src.core.settings import load_settings
from backend.src.models.base import Base
# Ensure model metadata is registered before creating tables.
from backend.src.models import approval_step, audit_log, document, user  # pylint: disable=unused-import

settings = load_settings()
DATABASE_URL = settings.database_url
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
    """Yield a SQLAlchemy session and close it after use."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
