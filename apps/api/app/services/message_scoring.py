"""Suspicious message heuristics (FR-043) — text only, PII-minimized storage."""

from __future__ import annotations

import re
from hashlib import sha256
from typing import Any
from uuid import uuid4

from app.models.schemas import Reason, Verdict
from app.services.hunting import attach_hunting
from app.services.scoring import (
    EMERGENCY_KEYWORDS,
    GOV_KEYWORDS,
    PAYMENT_KEYWORDS,
    _verdict_from_score,
)
from app.services.store import store
from app.services.store_models import utcnow

JOB_SCAM_PATTERNS = (
    r"kuniga\s*\d+",
    r"\$\s*\d+",
    r"ish\s*topish",
    r"удал[её]нн",
    r"заработ",
    r"telegram.*bonus",
    r"@\w+_bot",
)

SCAM_FAMILY_TELEGRAM_JOB = "telegram_job_scam"


def _redact_preview(text: str, limit: int = 160) -> str:
    redacted = re.sub(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "[email]", text, flags=re.I)
    redacted = re.sub(r"\+?\d[\d\s\-()]{7,}\d", "[phone]", redacted)
    return redacted[:limit]


def score_message(text: str, entities: dict[str, Any] | None = None) -> dict[str, Any]:
    body = text.strip()
    lower = body.lower()
    reasons: list[Reason] = []
    mitre: list[str] = ["T1566"]
    score = 10
    scam_family: str | None = None
    actor_hint: str | None = None

    for pat in JOB_SCAM_PATTERNS:
        if re.search(pat, lower, re.I):
            score += 35
            reasons.append(Reason(code="MSG_JOB_SCAM", message_key="reason.msg_job_scam"))
            scam_family = SCAM_FAMILY_TELEGRAM_JOB
            actor_hint = "uz_telegram_job_seed"
            break

    if any(k in lower for k in PAYMENT_KEYWORDS):
        score += 20
        reasons.append(Reason(code="MSG_PAYMENT_LURE", message_key="reason.msg_payment"))
        scam_family = scam_family or "payment_scam"

    if any(k in lower for k in GOV_KEYWORDS):
        score += 25
        reasons.append(Reason(code="MSG_GOV_LURE", message_key="reason.msg_gov"))
        scam_family = scam_family or "gov_impersonation"

    if any(k in lower for k in EMERGENCY_KEYWORDS):
        score += 20
        reasons.append(Reason(code="MSG_URGENCY", message_key="reason.msg_urgency"))
        scam_family = scam_family or "emergency_scam"

    ents = entities or {}
    urls = ents.get("urls") or []
    bot = ents.get("bot_username")
    if urls:
        score += 15
        reasons.append(Reason(code="MSG_HAS_URL", message_key="reason.msg_url"))
    if bot or re.search(r"@\w+", body):
        score += 15
        reasons.append(Reason(code="MSG_BOT_HANDLE", message_key="reason.msg_bot"))
        scam_family = scam_family or SCAM_FAMILY_TELEGRAM_JOB

    score = max(0, min(100, score))
    verdict, action, confidence = _verdict_from_score(score)
    if verdict == Verdict.clean and not reasons:
        reasons.append(Reason(code="MSG_NO_HIT", message_key="reason.msg_clean"))

    payload = {
        "score": score,
        "confidence": confidence,
        "verdict": verdict,
        "reasons": reasons,
        "mitre_tags": sorted(set(mitre)),
        "scam_family": scam_family,
        "actor_hint": actor_hint,
        "recommended_action": action,
        "text_hash": sha256(body.encode("utf-8")).hexdigest(),
        "preview": _redact_preview(body),
    }
    return attach_hunting(payload, subject_key=payload["text_hash"][:16])


def report_suspicious_message(
    text: str,
    source: str,
    entities: dict[str, Any] | None,
    user_id,
) -> dict[str, Any]:
    result = score_message(text, entities)
    report_id = uuid4()
    store.add_message_report(
        report_id=report_id,
        user_id=user_id,
        source=source,
        text_hash=result["text_hash"],
        preview=result["preview"],
        score=result["score"],
        scam_family=result["scam_family"],
        meta={
            "intent_tags": result["intent_tags"],
            "campaign_id": result["campaign_id"],
            "entity_url_count": len((entities or {}).get("urls") or []),
            "has_bot": bool((entities or {}).get("bot_username")),
        },
    )
    store.audit(
        user_id,
        "message.reported",
        {"report_id": str(report_id), "score": result["score"], "source": source},
    )
    from app.services.threat_events import emit_threat_event

    emit_threat_event(
        user_id=user_id,
        category="message",
        score=result["score"],
        subject_hash=result["text_hash"],
        mitre_tags=result["mitre_tags"],
        meta={"scam_family": result["scam_family"], "report_id": str(report_id)},
    )
    return {
        "report_id": report_id,
        "score": result["score"],
        "confidence": result["confidence"],
        "verdict": result["verdict"],
        "reasons": result["reasons"],
        "mitre_tags": result["mitre_tags"],
        "scam_family": result["scam_family"],
        "actor_hint": result["actor_hint"],
        "recommended_action": result["recommended_action"],
        "intent_tags": result["intent_tags"],
        "campaign_id": result["campaign_id"],
        "kill_chain_stage": result["kill_chain_stage"],
        "preview": result["preview"],
        "reported_at": utcnow(),
    }
