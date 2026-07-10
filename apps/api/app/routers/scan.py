from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

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
from app.http_status import UNPROCESSABLE
from app.services.auth import get_optional_user
from app.services.rate_limit import client_key, guest_limiter
from app.services.scoring import combine_risk, scan_file_hash, scan_qr, scan_url

router = APIRouter(tags=["scan"])


def _enforce_guest_limit(request: Request, response: Response, user) -> None:
    if user is None:
        headers = guest_limiter.check(client_key(request))
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
    _ = body.run_yara
    try:
        return scan_file_hash(
            body.sha256,
            file_name=body.file_name,
            user_id=user.id if user else None,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=UNPROCESSABLE,
            detail="Invalid SHA-256",
        ) from exc


@router.post("/risk-score", response_model=RiskScoreResponse)
def risk_score(body: RiskScoreRequest) -> RiskScoreResponse:
    result = combine_risk(body.features)
    return RiskScoreResponse(**result)
