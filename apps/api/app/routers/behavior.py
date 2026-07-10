from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.services.auth import get_current_user
from app.services.behavior import analyze_behavior

router = APIRouter(prefix="/behavior", tags=["behavior"])


class BehaviorWindow(BaseModel):
    scans: int
    threat_events: int
    malicious_scans: int
    critical_events: int


class BehaviorAnalyzeResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    verdict: str
    confidence: float
    recommended_action: str
    reasons: list[dict[str, str]]
    mitre_tags: list[str]
    window: BehaviorWindow
    model_version: str
    defensive_only: bool = True


@router.post("/analyze", response_model=BehaviorAnalyzeResponse)
def behavior_analyze(
    limit: int = Query(default=50, ge=5, le=100),
    user=Depends(get_current_user),
) -> BehaviorAnalyzeResponse:
    """Correlate recent scans/threat events (FR-080). Detection only."""
    result = analyze_behavior(user.id, window_limit=limit)
    return BehaviorAnalyzeResponse(**result)
