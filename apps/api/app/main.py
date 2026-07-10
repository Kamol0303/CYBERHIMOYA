from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings
from app.models.schemas import HealthResponse
from app.routers import auth, consents, feed, scan

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Cyber Guardian AI V1 — defensive-only API. "
        "No offensive, exploit, C2, or active probing capabilities."
    ),
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = FastAPI()
api.include_router(auth.router)
api.include_router(auth.me_router)
api.include_router(consents.router)
api.include_router(scan.router)
api.include_router(feed.router)
app.mount("/v1", api)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__, defensive_only=True)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "api": "/v1",
        "defensive_only": True,
    }
