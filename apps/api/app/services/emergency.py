from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from app.config import settings
from app.services.store import store
from app.services.store_models import EmergencyLogRow, utcnow

# In-memory confirm tokens (TTL). Production: Redis.
_CONFIRM_TOKENS: dict[str, dict] = {}


@dataclass
class AllowlistStatus:
    aq039_resolved: bool
    sms_destinations: list[str]
    api_endpoints: list[str]
    email_destinations: list[str]
    dry_run_forced: bool
    note: str


def allowlist_status() -> AllowlistStatus:
    sms = [x.strip() for x in settings.emergency_sms_allowlist.split(",") if x.strip()]
    apis = [x.strip() for x in settings.emergency_api_allowlist.split(",") if x.strip()]
    emails = [x.strip() for x in settings.emergency_email_allowlist.split(",") if x.strip()]
    # Filter obvious placeholders
    def real(items: list[str]) -> list[str]:
        return [i for i in items if not i.upper().startswith("PENDING") and i != "AQ-039"]

    sms_r, api_r, email_r = real(sms), real(apis), real(emails)
    resolved = bool(sms_r or api_r or email_r)
    return AllowlistStatus(
        aq039_resolved=resolved,
        sms_destinations=sms_r,
        api_endpoints=api_r,
        email_destinations=email_r,
        dry_run_forced=settings.emergency_dry_run or not resolved,
        note=(
            "AQ-039 unresolved: live dispatch disabled; dry-run logs only."
            if not resolved
            else "Allowlist configured; live dispatch still gated by CGA_EMERGENCY_DRY_RUN."
        ),
    )


def evaluate_critical(modules: list[str], confidence: float) -> tuple[bool, str]:
    unique = sorted({m.strip() for m in modules if m and m.strip()})
    if len(unique) < settings.emergency_min_modules:
        return False, f"Need ≥{settings.emergency_min_modules} independent modules"
    if confidence < settings.emergency_min_confidence:
        return False, f"Confidence below {settings.emergency_min_confidence}"
    return True, "ok"


def anonymized_user_ref(user_id: UUID) -> str:
    digest = hashlib.sha256(f"cga-em|{user_id}".encode()).hexdigest()[:16]
    return f"u_{digest}"


def make_evidence_code() -> str:
    return f"EV-{secrets.token_hex(4).upper()}"


def create_confirm_token(
    user_id: UUID,
    modules: list[str],
    confidence: float,
    incident_ref: str | None,
) -> dict:
    ok, reason = evaluate_critical(modules, confidence)
    if not ok:
        raise ValueError(reason)
    if not store.has_emergency_consent(user_id):
        raise PermissionError("emergency_consent_required")
    token = secrets.token_urlsafe(24)
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.emergency_confirm_ttl_minutes)
    _CONFIRM_TOKENS[token] = {
        "user_id": str(user_id),
        "modules": sorted({m.strip() for m in modules if m.strip()}),
        "confidence": confidence,
        "incident_ref": incident_ref,
        "exp": exp.isoformat(),
    }
    store.audit(
        user_id,
        "emergency.confirm_issued",
        {"modules": _CONFIRM_TOKENS[token]["modules"], "confidence": confidence},
    )
    return {
        "confirm_token": token,
        "expires_at": exp,
        "modules": _CONFIRM_TOKENS[token]["modules"],
        "requires_second_confirm": True,
    }


def dispatch(
    user_id: UUID,
    confirm_token: str,
    channel: str,
) -> EmergencyLogRow:
    entry = _CONFIRM_TOKENS.get(confirm_token)
    if not entry or entry["user_id"] != str(user_id):
        raise PermissionError("invalid_confirm_token")
    exp = datetime.fromisoformat(entry["exp"])
    if datetime.now(timezone.utc) > exp:
        _CONFIRM_TOKENS.pop(confirm_token, None)
        raise PermissionError("confirm_token_expired")
    if not store.has_emergency_consent(user_id):
        raise PermissionError("emergency_consent_required")

    status_info = allowlist_status()
    dry_run = status_info.dry_run_forced
    evidence = make_evidence_code()
    channel = channel.strip().lower()
    if channel not in {"sms", "api", "email"}:
        raise ValueError("invalid_channel")

    # Live path only if allowlist has destinations for channel and dry_run off.
    live_ok = False
    if not dry_run:
        if channel == "sms" and status_info.sms_destinations:
            live_ok = True
        elif channel == "api" and status_info.api_endpoints:
            live_ok = True
        elif channel == "email" and status_info.email_destinations:
            live_ok = True
        if not live_ok:
            dry_run = True

    payload_meta = {
        "anonymized_user_ref": anonymized_user_ref(user_id),
        "evidence_code": evidence,
        "modules": entry["modules"],
        "confidence": entry["confidence"],
        "incident_ref": entry.get("incident_ref"),
        "aq039_resolved": status_info.aq039_resolved,
        # Explicitly no raw PII/SMS/password (FR-EM06)
        "pii_included": False,
    }

    status = "dry_run_logged" if dry_run else "queued_allowlisted"
    # We never actually send SMS/email in this codebase without AQ-039 + explicit non-dry-run.
    # Even "queued_allowlisted" only records intent for an external worker.
    row = EmergencyLogRow(
        id=uuid4(),
        user_id=user_id,
        status=status,
        channel=channel,
        evidence_code=evidence,
        modules=entry["modules"],
        confidence=float(entry["confidence"]),
        dry_run=dry_run,
        meta=payload_meta,
        created_at=utcnow(),
    )
    store.add_emergency_log(row)
    store.audit(user_id, "emergency.dispatch", {"status": status, "channel": channel, "dry_run": dry_run})
    _CONFIRM_TOKENS.pop(confirm_token, None)
    return row


def clear_confirm_tokens() -> None:
    _CONFIRM_TOKENS.clear()
