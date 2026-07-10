"""In-app notifications (FR-091) — body keys only, no raw PII."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from app.services.store import store
from app.services.store_models import NotificationRow, utcnow


def dispatch_notification(
    *,
    user_id: UUID,
    level: str,
    body_key: str,
    body_params: dict[str, Any] | None = None,
    subject_hash: str | None = None,
    related_event_id: UUID | None = None,
) -> NotificationRow:
    row = NotificationRow(
        id=uuid4(),
        user_id=user_id,
        level=level,
        body_key=body_key,
        body_params=body_params or {},
        subject_hash=subject_hash,
        related_event_id=related_event_id,
        read_at=None,
        created_at=utcnow(),
    )
    store.add_notification(row)
    return row
