from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.schemas import NotificationItem
from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationItem])
def list_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    user=Depends(get_current_user),
) -> list[NotificationItem]:
    rows = store.list_notifications(user.id, unread_only=unread_only, limit=limit)
    return [
        NotificationItem(
            id=r.id,
            level=r.level,
            body_key=r.body_key,
            body_params=r.body_params,
            subject_hash=r.subject_hash,
            related_event_id=r.related_event_id,
            read_at=r.read_at,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/{notification_id}/read", response_model=NotificationItem)
def mark_read(notification_id: UUID, user=Depends(get_current_user)) -> NotificationItem:
    ok = store.mark_notification_read(user.id, notification_id)
    if not ok:
        # Already read or missing — still try to return current row
        rows = store.list_notifications(user.id, unread_only=False, limit=200)
        match = next((r for r in rows if r.id == notification_id), None)
        if match is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        r = match
    else:
        rows = store.list_notifications(user.id, unread_only=False, limit=200)
        r = next(x for x in rows if x.id == notification_id)
    return NotificationItem(
        id=r.id,
        level=r.level,
        body_key=r.body_key,
        body_params=r.body_params,
        subject_hash=r.subject_hash,
        related_event_id=r.related_event_id,
        read_at=r.read_at,
        created_at=r.created_at,
    )
