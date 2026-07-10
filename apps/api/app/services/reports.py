"""JSON reports export (FR-093) — PII-redacted aggregates."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from app.services.store import store
from app.services.store_models import ReportRow, utcnow


def _parse(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).replace(tzinfo=None)


def build_report(
    *,
    user_id: UUID,
    from_iso: str,
    to_iso: str,
    types: list[str],
    redact_pii: bool = True,
) -> ReportRow:
    start = _parse(from_iso)
    end = _parse(to_iso)
    payload: dict[str, Any] = {
        "from": from_iso,
        "to": to_iso,
        "types": types,
        "redact_pii": redact_pii,
        "generated_at": utcnow().isoformat(),
        "sections": {},
    }
    if "scan" in types:
        scans = store.list_scans(user_id=user_id, limit=200)
        items = []
        for s in scans:
            if not (start <= s.created_at.replace(tzinfo=None) <= end):
                continue
            items.append(
                {
                    "scan_id": str(s.id),
                    "scan_type": s.scan_type,
                    "score": s.score,
                    "verdict": s.verdict,
                    "subject_hash": s.subject_hash if not redact_pii else s.subject_hash[:12],
                    "scam_family": s.meta.get("scam_family"),
                    "created_at": s.created_at.isoformat(),
                }
            )
        payload["sections"]["scan"] = {"count": len(items), "items": items}
    if "threat_event" in types:
        events = store.list_threat_events(user_id, limit=200)
        items = []
        for e in events:
            if not (start <= e.detected_at.replace(tzinfo=None) <= end):
                continue
            items.append(
                {
                    "event_id": str(e.id),
                    "category": e.category,
                    "severity": e.severity,
                    "subject_hash": e.subject_hash if not redact_pii else e.subject_hash[:12],
                    "detected_at": e.detected_at.isoformat(),
                }
            )
        payload["sections"]["threat_event"] = {"count": len(items), "items": items}

    row = ReportRow(
        id=uuid4(),
        user_id=user_id,
        status="ready",
        payload=payload,
        created_at=utcnow(),
    )
    store.add_report(row)
    store.audit(user_id, "report.created", {"report_id": str(row.id), "types": types})
    return row
