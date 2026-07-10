from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.schemas import ThreatEventItem
from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(prefix="/threat-events", tags=["threat-events"])


@router.get("", response_model=list[ThreatEventItem])
def list_events(
    severity: str | None = Query(default=None, pattern="^(info|warning|critical)$"),
    limit: int = Query(default=50, ge=1, le=100),
    user=Depends(get_current_user),
) -> list[ThreatEventItem]:
    rows = store.list_threat_events(user.id, limit=limit, severity=severity)
    return [
        ThreatEventItem(
            event_id=r.id,
            category=r.category,
            severity=r.severity,
            subject_hash=r.subject_hash,
            mitre_tags=r.mitre_tags,
            score=r.meta.get("score"),
            scam_family=r.meta.get("scam_family"),
            detected_at=r.detected_at,
        )
        for r in rows
    ]


@router.get("/{event_id}", response_model=ThreatEventItem)
def get_event(event_id: UUID, user=Depends(get_current_user)) -> ThreatEventItem:
    r = store.get_threat_event(user.id, event_id)
    if r is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return ThreatEventItem(
        event_id=r.id,
        category=r.category,
        severity=r.severity,
        subject_hash=r.subject_hash,
        mitre_tags=r.mitre_tags,
        score=r.meta.get("score"),
        scam_family=r.meta.get("scam_family"),
        detected_at=r.detected_at,
    )
