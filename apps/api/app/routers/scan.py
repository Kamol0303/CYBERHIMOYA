from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.models.schemas import (
    RiskScoreRequest,
    RiskScoreResponse,
    UrlScanRequest,
    UrlScanResponse,
)
from app.services.auth import get_optional_user
from app.services.scoring import combine_risk, scan_url

router = APIRouter(tags=["scan"])


@router.post("/scan/url", response_model=UrlScanResponse)
def scan_url_endpoint(
    body: UrlScanRequest,
    request: Request,
    user=Depends(get_optional_user),
) -> UrlScanResponse:
    # Guest scans allowed; authenticated scans attach user_id for history.
    _ = request  # reserved for rate-limit middleware hooks
    return scan_url(body.url, user_id=user.id if user else None)


@router.post("/risk-score", response_model=RiskScoreResponse)
def risk_score(body: RiskScoreRequest) -> RiskScoreResponse:
    result = combine_risk(body.features)
    return RiskScoreResponse(**result)
