"""Threat event emission (FR-092) — authenticated suspicious/malicious only."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from app.services.store import store
from app.services.store_models import ThreatEventRow, utcnow


def severity_for_score(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 50:
        return "warning"
    return "info"


def emit_threat_event(
    *,
    user_id: UUID | None,
    category: str,
    score: int,
    subject_hash: str,
    mitre_tags: list[str],
    meta: dict[str, Any],
) -> ThreatEventRow | None:
    if user_id is None or score < 50:
        return None
    # Dedup: same user + subject within 15 minutes
    if store.find_recent_threat_event(user_id, subject_hash, within_seconds=900):
        return None
    severity = severity_for_score(score)
    row = ThreatEventRow(
        id=uuid4(),
        user_id=user_id,
        category=category,
        severity=severity,
        subject_hash=subject_hash,
        mitre_tags=mitre_tags,
        meta={**meta, "score": score},
        detected_at=utcnow(),
    )
    store.add_threat_event(row)
    from app.services.notifications import dispatch_notification

    dispatch_notification(
        user_id=user_id,
        level=severity,
        body_key=f"notify.threat.{severity}",
        body_params={"category": category, "score": score},
        subject_hash=subject_hash,
        related_event_id=row.id,
    )
    return row
