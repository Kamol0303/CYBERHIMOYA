"""Passive hunting metadata helpers (FR-MX01) — defensive tags only."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid5, NAMESPACE_URL


def campaign_id_for(*, scam_family: str | None, subject_key: str | None) -> str | None:
    """Stable campaign id from family + subject (domain/hash). Not random per request."""
    if not scam_family and not subject_key:
        return None
    key = f"{scam_family or 'unknown'}|{(subject_key or '').lower()}"
    return str(uuid5(NAMESPACE_URL, f"cga-campaign:{key}"))


def intent_tags_for(
    *,
    scam_family: str | None,
    reasons: list[Any],
    mitre_tags: list[str],
) -> list[str]:
    tags: set[str] = set()
    codes = {getattr(r, "code", None) or (r.get("code") if isinstance(r, dict) else None) for r in reasons}
    if "TI_DOMAIN_HIT" in codes or "TI_HASH_HIT" in codes:
        tags.add("phishing")
    if scam_family == "payment_scam" or "UZ_FAKE_PAYMENT" in codes:
        tags.add("payment_fraud")
    if scam_family == "gov_impersonation" or "UZ_FAKE_GOV" in codes:
        tags.add("gov_impersonation")
    if scam_family == "emergency_scam" or "EMERGENCY_LURE" in codes:
        tags.add("urgency_lure")
    if scam_family in {"fake_bank_apk", "trojan_dropper_seed"} or "APK_NAME_HEURISTIC" in codes:
        tags.add("malware_drop")
    if "T1566" in mitre_tags:
        tags.add("phishing")
    if "T1204" in mitre_tags:
        tags.add("user_execution")
    return sorted(tags)


def kill_chain_stage_for(score: int) -> str | None:
    if score >= 50:
        return "delivery"
    return None


def attach_hunting(
    payload: dict[str, Any],
    *,
    subject_key: str | None,
) -> dict[str, Any]:
    family = payload.get("scam_family")
    reasons = payload.get("reasons") or []
    mitre = payload.get("mitre_tags") or []
    score = int(payload.get("score") or 0)
    payload["intent_tags"] = intent_tags_for(
        scam_family=family, reasons=reasons, mitre_tags=mitre
    )
    payload["campaign_id"] = campaign_id_for(scam_family=family, subject_key=subject_key)
    payload["kill_chain_stage"] = kill_chain_stage_for(score)
    return payload
