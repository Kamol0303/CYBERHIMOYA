from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import ConsentRecord, ConsentUpsert
from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(prefix="/consents", tags=["consents"])


@router.get("", response_model=list[ConsentRecord])
def list_consents(user=Depends(get_current_user)) -> list[ConsentRecord]:
    return [
        ConsentRecord(
            id=r.id,
            user_id=r.user_id,
            consent_type=r.consent_type,  # type: ignore[arg-type]
            granted=r.granted,
            changed_at=r.changed_at,
            source=r.source,
        )
        for r in store.list_consents(user.id)
    ]


@router.post("", response_model=ConsentRecord)
def upsert_consent(body: ConsentUpsert, user=Depends(get_current_user)) -> ConsentRecord:
    row = store.upsert_consent(user.id, body.consent_type.value, body.granted, body.source)
    return ConsentRecord(
        id=row.id,
        user_id=row.user_id,
        consent_type=row.consent_type,  # type: ignore[arg-type]
        granted=row.granted,
        changed_at=row.changed_at,
        source=row.source,
    )
