from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.models.schemas import ScanHistoryItem
from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(prefix="/scans", tags=["scans"])


@router.get("", response_model=list[ScanHistoryItem])
def list_my_scans(
    limit: int = Query(default=20, ge=1, le=100),
    user=Depends(get_current_user),
) -> list[ScanHistoryItem]:
    rows = store.list_scans(user_id=user.id, limit=limit)
    items: list[ScanHistoryItem] = []
    for row in rows:
        items.append(
            ScanHistoryItem(
                scan_id=row.id,
                scan_type=row.scan_type,
                score=row.score,
                verdict=row.verdict,
                subject_hash=row.subject_hash,
                mitre_tags=row.mitre_tags,
                scam_family=row.meta.get("scam_family"),
                recommended_action=row.meta.get("recommended_action"),
                intent_tags=list(row.meta.get("intent_tags") or []),
                campaign_id=row.meta.get("campaign_id"),
                created_at=row.created_at,
            )
        )
    return items
