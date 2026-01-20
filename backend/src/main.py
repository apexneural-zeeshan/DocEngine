import backend.src.models  # noqa: F401
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.src.core.config import load_settings
from backend.src.api.approvals import router as approvals_router
from backend.src.api.documents import router as documents_router
from backend.src.db.base import Base
from backend.src.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    app.state.settings = settings
    app.title = settings.app_name
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(documents_router)
app.include_router(approvals_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "OK"}

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
