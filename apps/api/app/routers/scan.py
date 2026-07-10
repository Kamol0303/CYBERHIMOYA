from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.schemas import (
    FileScanRequest,
    FileScanResponse,
    QrScanRequest,
    QrScanResponse,
    RiskScoreRequest,
    RiskScoreResponse,
    UrlScanRequest,
    UrlScanResponse,
)
from app.services.auth import get_optional_user
from app.services.scoring import combine_risk, scan_file_hash, scan_qr, scan_url

router = APIRouter(tags=["scan"])


@router.post("/scan/url", response_model=UrlScanResponse)
def scan_url_endpoint(
    body: UrlScanRequest,
    request: Request,
    user=Depends(get_optional_user),
) -> UrlScanResponse:
    _ = request
    return scan_url(body.url, user_id=user.id if user else None)


@router.post("/scan/qr", response_model=QrScanResponse)
def scan_qr_endpoint(
    body: QrScanRequest,
    user=Depends(get_optional_user),
) -> QrScanResponse:
    return scan_qr(body.payload_text, user_id=user.id if user else None)


@router.post("/scan/file", response_model=FileScanResponse)
def scan_file_endpoint(
    body: FileScanRequest,
    user=Depends(get_optional_user),
) -> FileScanResponse:
    # Prefer client-side hash — no binary upload required for V1 hash path.
    _ = body.run_yara  # reserved; YARA offline packs land later
    try:
        return scan_file_hash(
            body.sha256,
            file_name=body.file_name,
            user_id=user.id if user else None,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid SHA-256",
        ) from exc


@router.post("/risk-score", response_model=RiskScoreResponse)
def risk_score(body: RiskScoreRequest) -> RiskScoreResponse:
    result = combine_risk(body.features)
    return RiskScoreResponse(**result)
