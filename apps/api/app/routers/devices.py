from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import DeviceRecord, DeviceRegisterRequest
from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register", response_model=DeviceRecord)
def register_device(body: DeviceRegisterRequest, user=Depends(get_current_user)) -> DeviceRecord:
    fingerprint = (body.fingerprint or "").strip() or f"auto-{uuid4().hex[:16]}"
    row = store.upsert_device(
        user.id,
        body.platform,
        body.app_version,
        fingerprint,
        body.device_label,
    )
    store.audit(
        user.id,
        "device.registered",
        {"device_id": str(row.id), "platform": row.platform},
    )
    return DeviceRecord(
        id=row.id,
        platform=row.platform,
        app_version=row.app_version,
        device_label=row.device_label,
        fingerprint=row.fingerprint,
        created_at=row.created_at,
        last_seen_at=row.last_seen_at,
    )


@router.get("", response_model=list[DeviceRecord])
def list_devices(user=Depends(get_current_user)) -> list[DeviceRecord]:
    return [
        DeviceRecord(
            id=r.id,
            platform=r.platform,
            app_version=r.app_version,
            device_label=r.device_label,
            fingerprint=r.fingerprint,
            created_at=r.created_at,
            last_seen_at=r.last_seen_at,
        )
        for r in store.list_devices(user.id)
    ]


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_device(device_id: UUID, user=Depends(get_current_user)) -> None:
    ok = store.delete_device(user.id, device_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    store.audit(user.id, "device.revoked", {"device_id": str(device_id)})
