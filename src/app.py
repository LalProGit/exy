from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import get_settings
from src.core.logging import configure_logging
from src.api.router import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    yield


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api")
    return app
