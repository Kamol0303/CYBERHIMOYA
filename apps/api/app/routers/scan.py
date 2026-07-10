from __future__ import annotations

from hashlib import sha256
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from app.models.schemas import (
    FileScanRequest,
    FileScanResponse,
    QrScanRequest,
    QrScanResponse,
    RiskScoreHistoryItem,
    RiskScoreRequest,
    RiskScoreResponse,
    UrlScanRequest,
    UrlScanResponse,
)
from app.http_status import UNPROCESSABLE
from app.services.auth import get_current_user, get_optional_user
from app.services.rate_limit import client_key, guest_limiter
from app.services.scoring import combine_risk, scan_file_hash, scan_qr, scan_url
from app.services.store import store
from app.services.store_models import RiskScoreHistoryRow, utcnow

router = APIRouter(tags=["scan"])


def _enforce_guest_limit(request: Request, response: Response, user) -> None:
    if user is None:
        headers = guest_limiter.check(client_key(request), instance=request.url.path)
        for k, v in headers.items():
            response.headers[k] = v


@router.post("/scan/url", response_model=UrlScanResponse)
def scan_url_endpoint(
    body: UrlScanRequest,
    request: Request,
    response: Response,
    user=Depends(get_optional_user),
) -> UrlScanResponse:
    _enforce_guest_limit(request, response, user)
    return scan_url(body.url, user_id=user.id if user else None)


@router.post("/scan/qr", response_model=QrScanResponse)
def scan_qr_endpoint(
    body: QrScanRequest,
    request: Request,
    response: Response,
    user=Depends(get_optional_user),
) -> QrScanResponse:
    _enforce_guest_limit(request, response, user)
    return scan_qr(body.payload_text, user_id=user.id if user else None)


@router.post("/scan/file", response_model=FileScanResponse)
def scan_file_endpoint(
    body: FileScanRequest,
    request: Request,
    response: Response,
    user=Depends(get_optional_user),
) -> FileScanResponse:
    _enforce_guest_limit(request, response, user)
    try:
        return scan_file_hash(
            body.sha256,
            file_name=body.file_name,
            user_id=user.id if user else None,
            run_yara=body.run_yara,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=UNPROCESSABLE,
            detail="Invalid SHA-256",
        ) from exc


@router.post("/risk-score", response_model=RiskScoreResponse)
def risk_score(
    body: RiskScoreRequest,
    user=Depends(get_optional_user),
) -> RiskScoreResponse:
    result = combine_risk(body.features)
    if user is not None:
        subject_key = body.subject_id or json_safe_features(body.features)
        store.add_risk_score_history(
            RiskScoreHistoryRow(
                id=uuid4(),
                user_id=user.id,
                subject_type=body.subject_type,
                subject_hash=sha256(subject_key.encode("utf-8")).hexdigest(),
                score=result["score"],
                confidence=float(result["confidence"]),
                model_version=str(result.get("model_version") or "score-2026.07.1"),
                created_at=utcnow(),
            )
        )
    return RiskScoreResponse(**result)


def json_safe_features(features: dict) -> str:
    # Stable-ish fingerprint without raw PII — keys sorted.
    parts = []
    for k in sorted(features.keys()):
        parts.append(f"{k}={features[k]}")
    return "|".join(parts)


@router.get("/risk-score/history", response_model=list[RiskScoreHistoryItem], tags=["scan"])
def risk_score_history(
    limit: int = Query(default=50, ge=1, le=100),
    user=Depends(get_current_user),
) -> list[RiskScoreHistoryItem]:
    rows = store.list_risk_score_history(user.id, limit=limit)
    return [
        RiskScoreHistoryItem(
            id=r.id,
            subject_type=r.subject_type,
            subject_hash=r.subject_hash,
            score=r.score,
            confidence=r.confidence,
            model_version=r.model_version,
            created_at=r.created_at,
        )
        for r in rows
    ]
