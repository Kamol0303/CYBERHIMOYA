from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.models.schemas import Reason, ScanHistoryItem
from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(prefix="/scans", tags=["scans"])


class ScanDetailResponse(BaseModel):
    scan_id: UUID
    scan_type: str
    score: int
    verdict: str
    subject_hash: str
    mitre_tags: list[str]
    scam_family: str | None = None
    recommended_action: str | None = None
    intent_tags: list[str] = Field(default_factory=list)
    campaign_id: str | None = None
    reasons: list[Reason] = Field(default_factory=list)
    kill_chain_stage: str | None = None
    created_at: datetime


@router.get("", response_model=list[ScanHistoryItem])
def list_my_scans(
    limit: int = Query(default=20, ge=1, le=100),
    verdict: str | None = Query(default=None, pattern="^(malicious|suspicious|clean|unknown)$"),
    scan_type: str | None = Query(default=None, pattern="^(url|qr|file|message)$"),
    user=Depends(get_current_user),
) -> list[ScanHistoryItem]:
    rows = store.list_scans(
        user_id=user.id, limit=limit, verdict=verdict, scan_type=scan_type
    )
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


@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan_detail(scan_id: UUID, user=Depends(get_current_user)) -> ScanDetailResponse:
    row = store.get_scan(user.id, scan_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    reasons = [Reason(**r) if isinstance(r, dict) else r for r in (row.reasons or [])]
    return ScanDetailResponse(
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
        reasons=reasons,
        kill_chain_stage=row.meta.get("kill_chain_stage"),
        created_at=row.created_at,
    )
