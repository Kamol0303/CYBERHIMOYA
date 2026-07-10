from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.config import settings
from app.models.schemas import HealthResponse
from app.routers import auth, consents, emergency, feed, scan, scans
from app.services.feed import FEEDS_DIR, ensure_feed_files

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
api.include_router(scans.router)
api.include_router(feed.router)
api.include_router(emergency.router)
app.mount("/v1", api)

# Local threat-feed CDN stub (signed JSON packs only).
FEEDS_DIR.mkdir(parents=True, exist_ok=True)
ensure_feed_files()
app.mount("/cdn/feeds", StaticFiles(directory=str(FEEDS_DIR)), name="feed_cdn")


def _storage_label() -> str:
    url = settings.database_url
    if url.startswith("sqlite"):
        return "sqlite"
    if url.startswith("postgres"):
        return "postgresql"
    return "unknown"


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=__version__,
        defensive_only=True,
        storage=_storage_label(),
    )


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "api": "/v1",
        "feed_cdn": "/cdn/feeds",
        "defensive_only": True,
        "storage": _storage_label(),
    }
