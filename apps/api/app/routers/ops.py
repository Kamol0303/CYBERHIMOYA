from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app import __version__
from app.config import settings
from app.models.schemas import MetricsResponse
from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(tags=["ops"])


@router.get("/metrics", response_model=MetricsResponse)
def metrics() -> MetricsResponse:
    """Lightweight ops snapshot — no PII."""
    threat_n = 0
    notif_n = 0
    allow_n = 0
    try:
        conn = getattr(store, "_conn", None)
        if conn is not None and hasattr(conn, "execute"):
            threat_n = conn.execute("SELECT COUNT(*) AS c FROM threat_events").fetchone()["c"]
            notif_n = conn.execute("SELECT COUNT(*) AS c FROM notifications").fetchone()["c"]
            allow_n = conn.execute("SELECT COUNT(*) AS c FROM domain_allowlist").fetchone()["c"]
    except Exception:
        threat_n = notif_n = allow_n = 0
    return MetricsResponse(
        version=__version__,
        environment=settings.environment,
        defensive_only=True,
        emergency_dry_run=settings.emergency_dry_run,
        scan_rows=len(store.list_scans(limit=10_000)),
        feed_version=settings.feed_version,
        threat_event_rows=int(threat_n),
        notification_rows=int(notif_n),
        domain_allowlist_rows=int(allow_n),
    )


@router.post("/retention/prune")
def prune_retention(
    retain_days: int = Query(default=180, ge=1, le=3650),
    user=Depends(get_current_user),
) -> dict:
    """NFR-040 — prune aged risk_score_history rows (default 180 days)."""
    deleted = store.prune_risk_score_history(retain_days=retain_days)
    store.audit(
        user.id,
        "retention.prune_risk_history",
        {"deleted": deleted, "retain_days": retain_days},
    )
    return {
        "deleted_risk_history": deleted,
        "retain_days": retain_days,
        "defensive_only": True,
    }
