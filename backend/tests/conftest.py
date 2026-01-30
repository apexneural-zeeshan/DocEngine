import os
import backend.src.models  # noqa: E402,F401
import backend.src.main as main_app  # noqa: E402
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure tests use an in-memory database before importing app modules.
os.environ.setdefault("DOCENGINE_DATABASE_URL", "sqlite+pysqlite:///:memory:")


from backend.src.models.base import Base  # noqa: E402
from backend.src.db.session import get_session  # noqa: E402
from backend.src.main import app  # noqa: E402



@pytest.fixture(scope="session")
def engine():
    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    # Ensure startup events use the test engine, not the default one.
    main_app.engine = test_engine
    yield test_engine
    test_engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(session_factory):
    def override_get_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
