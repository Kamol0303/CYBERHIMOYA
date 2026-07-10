from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.schemas import (
    ConsentRecord,
    EmergencyAllowlistResponse,
    EmergencyConfirmRequest,
    EmergencyConfirmResponse,
    EmergencyConsentRequest,
    EmergencyDispatchRequest,
    EmergencyLogItem,
)
from app.services.auth import get_current_user
from app.services import emergency as em
from app.services.store import store

router = APIRouter(prefix="/emergency", tags=["emergency"])


@router.get("/allowlist", response_model=EmergencyAllowlistResponse)
def get_allowlist() -> EmergencyAllowlistResponse:
    """Public status of AQ-039 allowlist (no destination values leaked if pending)."""
    info = em.allowlist_status()
    return EmergencyAllowlistResponse(
        aq039_resolved=info.aq039_resolved,
        dry_run_forced=info.dry_run_forced,
        sms_destinations_configured=len(info.sms_destinations),
        api_endpoints_configured=len(info.api_endpoints),
        email_destinations_configured=len(info.email_destinations),
        note=info.note,
    )


@router.post("/consent", response_model=ConsentRecord)
def emergency_consent(body: EmergencyConsentRequest, user=Depends(get_current_user)) -> ConsentRecord:
    row = store.upsert_consent(
        user.id,
        "emergency_law_enforcement",
        body.granted,
        body.source,
    )
    return ConsentRecord(
        id=row.id,
        user_id=row.user_id,
        consent_type=row.consent_type,  # type: ignore[arg-type]
        granted=row.granted,
        changed_at=row.changed_at,
        source=row.source,
    )


@router.post("/confirm", response_model=EmergencyConfirmResponse)
def emergency_confirm(
    body: EmergencyConfirmRequest,
    user=Depends(get_current_user),
) -> EmergencyConfirmResponse:
    try:
        result = em.create_confirm_token(
            user.id,
            body.modules,
            body.confidence,
            body.incident_ref,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return EmergencyConfirmResponse(**result)


@router.post("/dispatch", response_model=EmergencyLogItem, status_code=status.HTTP_202_ACCEPTED)
def emergency_dispatch(
    body: EmergencyDispatchRequest,
    user=Depends(get_current_user),
) -> EmergencyLogItem:
    try:
        row = em.dispatch(user.id, body.confirm_token, body.channel)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return EmergencyLogItem(
        id=row.id,
        status=row.status,
        channel=row.channel,
        evidence_code=row.evidence_code,
        modules=row.modules,
        confidence=row.confidence,
        dry_run=row.dry_run,
        created_at=row.created_at,
    )


@router.get("/logs", response_model=list[EmergencyLogItem])
def emergency_logs(
    limit: int = Query(default=20, ge=1, le=100),
    user=Depends(get_current_user),
) -> list[EmergencyLogItem]:
    rows = store.list_emergency_logs(user.id, limit=limit)
    return [
        EmergencyLogItem(
            id=r.id,
            status=r.status,
            channel=r.channel,
            evidence_code=r.evidence_code,
            modules=r.modules,
            confidence=r.confidence,
            dry_run=r.dry_run,
            created_at=r.created_at,
        )
        for r in rows
    ]
