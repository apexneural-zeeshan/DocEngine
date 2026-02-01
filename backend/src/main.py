import backend.src.models  # noqa: F401
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.src.core.settings import validate_settings
from backend.src.api.approvals import router as approvals_router
from backend.src.api.auth import router as auth_router
from backend.src.api.documents import router as documents_router
from backend.src.db.base import Base
from backend.src.db.session import engine
from backend.src.api.dev import router as dev_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = validate_settings()
    app.state.settings = settings
    app.title = settings.app_name
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(documents_router)
app.include_router(approvals_router)
app.include_router(auth_router)
app.include_router(dev_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "OK"}
