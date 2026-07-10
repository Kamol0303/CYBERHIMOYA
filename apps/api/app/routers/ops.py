from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.config import settings
from app.services.store import store

router = APIRouter(tags=["ops"])


@router.get("/metrics")
def metrics() -> dict:
    """Lightweight ops snapshot — no PII."""
    return {
        "version": __version__,
        "environment": settings.environment,
        "defensive_only": True,
        "emergency_dry_run": settings.emergency_dry_run,
        "scan_rows": len(store.list_scans(limit=10_000)),
        "feed_version": settings.feed_version,
    }
