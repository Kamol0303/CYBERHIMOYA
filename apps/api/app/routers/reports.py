from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import ReportCreateRequest, ReportResponse
from app.services.auth import get_current_user
from app.services.reports import build_report
from app.services.store import store

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(body: ReportCreateRequest, user=Depends(get_current_user)) -> ReportResponse:
    row = build_report(
        user_id=user.id,
        from_iso=body.from_ts.isoformat(),
        to_iso=body.to_ts.isoformat(),
        types=body.types,
        redact_pii=body.redact_pii,
    )
    return ReportResponse(
        report_id=row.id,
        status=row.status,
        created_at=row.created_at,
        payload=row.payload,
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: UUID, user=Depends(get_current_user)) -> ReportResponse:
    row = store.get_report(user.id, report_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return ReportResponse(
        report_id=row.id,
        status=row.status,
        created_at=row.created_at,
        payload=row.payload,
    )
