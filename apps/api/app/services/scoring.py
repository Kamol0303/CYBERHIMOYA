from __future__ import annotations

import re
from hashlib import sha256
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from app.models.schemas import Reason, UrlScanResponse, Verdict
from app.services.store import ScanRow, store, utcnow

# Seed IOC / heuristic lists — defensive reputation only (no active probing).
KNOWN_MALICIOUS_DOMAINS = {
    "pay-click-uz.tk",
    "gov-subsidy-uz.xyz",
    "telegram-bonus-uz.ml",
    "iiv-fine-pay.ru.com",
    "click-payme-secure.cf",
}

KNOWN_SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz"}

PAYMENT_KEYWORDS = ("payme", "click", "uzum", "paynet", "humo", "uzcard", "to'lov", "tolov")
GOV_KEYWORDS = ("gov", "soliq", "iiv", "mygov", "subsidiya", "jarima", "passport")
EMERGENCY_KEYWORDS = ("emergency", "favqulodda", "yordam", "blokirovka", "hisobingiz")

SCAM_FAMILY_PAYMENT = "payment_scam"
SCAM_FAMILY_GOV = "gov_impersonation"
SCAM_FAMILY_EMERGENCY = "emergency_scam"


def normalize_url(raw: str) -> str:
    url = raw.strip()
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    path = parsed.path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    scheme = (parsed.scheme or "https").lower()
    return f"{scheme}://{host}{path}{query}"


def _domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def _subject_hash(url: str) -> str:
    return sha256(url.encode("utf-8")).hexdigest()


def score_url(url: str) -> dict[str, Any]:
    """Passive URL reputation + heuristic scoring. No outbound probing."""
    normalized = normalize_url(url)
    domain = _domain(normalized)
    reasons: list[Reason] = []
    mitre: list[str] = []
    score = 5
    scam_family: str | None = None
    actor_hint: str | None = None
    lower = normalized.lower()

    if domain in KNOWN_MALICIOUS_DOMAINS:
        score += 70
        reasons.append(Reason(code="TI_DOMAIN_HIT", message_key="reason.ti_domain_hit"))
        mitre.append("T1566")
        actor_hint = "uz_campaign_seed"

    for tld in KNOWN_SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            score += 25
            reasons.append(Reason(code="SUSPICIOUS_TLD", message_key="reason.suspicious_tld"))
            break

    if re.search(r"[^\x00-\x7f]", domain) or "xn--" in domain:
        score += 20
        reasons.append(Reason(code="PUNYCODE_OR_IDN", message_key="reason.punycode"))
        mitre.append("T1566.002")

    if len(domain) > 40 or domain.count("-") >= 3:
        score += 15
        reasons.append(Reason(code="LONG_OR_HYPHEN_DOMAIN", message_key="reason.long_domain"))

    if any(k in lower for k in PAYMENT_KEYWORDS) and domain not in {
        "payme.uz",
        "click.uz",
        "uzumbank.uz",
    }:
        score += 20
        scam_family = SCAM_FAMILY_PAYMENT
        reasons.append(Reason(code="UZ_FAKE_PAYMENT", message_key="reason.uz_fake_payment"))
        mitre.append("T1566")

    if any(k in lower for k in GOV_KEYWORDS) and not domain.endswith(".gov.uz"):
        score += 25
        scam_family = scam_family or SCAM_FAMILY_GOV
        reasons.append(Reason(code="UZ_FAKE_GOV", message_key="reason.uz_fake_gov"))
        mitre.append("T1566")

    if any(k in lower for k in EMERGENCY_KEYWORDS):
        score += 15
        scam_family = scam_family or SCAM_FAMILY_EMERGENCY
        reasons.append(Reason(code="EMERGENCY_LURE", message_key="reason.emergency_lure"))

    if "@" in normalized or "%40" in lower:
        score += 30
        reasons.append(Reason(code="CREDENTIAL_IN_URL", message_key="reason.credential_in_url"))

    score = max(0, min(100, score))
    if score >= 80:
        verdict = Verdict.malicious
        action = "block_and_warn"
        confidence = 0.88
    elif score >= 50:
        verdict = Verdict.suspicious
        action = "warn_and_review"
        confidence = 0.72
    elif score >= 20:
        verdict = Verdict.suspicious
        action = "caution"
        confidence = 0.55
    else:
        verdict = Verdict.clean
        action = "allow"
        confidence = 0.6
        if not reasons:
            reasons.append(Reason(code="NO_TI_HIT", message_key="reason.no_ti_hit"))

    mitre = sorted(set(mitre))
    return {
        "url_normalized": normalized,
        "score": score,
        "confidence": confidence,
        "verdict": verdict,
        "reasons": reasons,
        "mitre_tags": mitre,
        "scam_family": scam_family,
        "actor_hint": actor_hint,
        "recommended_action": action,
        "subject_hash": _subject_hash(normalized),
    }


def scan_url(url: str, user_id=None) -> UrlScanResponse:
    result = score_url(url)
    scan_id = uuid4()
    store.add_scan(
        ScanRow(
            id=scan_id,
            user_id=user_id,
            scan_type="url",
            score=result["score"],
            verdict=result["verdict"].value,
            reasons=[r.model_dump() for r in result["reasons"]],
            subject_hash=result["subject_hash"],
            mitre_tags=result["mitre_tags"],
            meta={
                "scam_family": result["scam_family"],
                "actor_hint": result["actor_hint"],
                "recommended_action": result["recommended_action"],
            },
            created_at=utcnow(),
        )
    )
    return UrlScanResponse(
        scan_id=scan_id,
        url_normalized=result["url_normalized"],
        score=result["score"],
        confidence=result["confidence"],
        verdict=result["verdict"],
        reasons=result["reasons"],
        mitre_tags=result["mitre_tags"],
        scam_family=result["scam_family"],
        actor_hint=result["actor_hint"],
        recommended_action=result["recommended_action"],
        scanned_at=utcnow(),
    )


def combine_risk(features: dict[str, Any]) -> dict[str, Any]:
    url_score = int(features.get("url_score") or 0)
    ti_hits = int(features.get("ti_hits") or 0)
    behavior = int(features.get("behavior_score") or 0)
    heuristics = features.get("local_heuristics") or []
    score = min(100, int(url_score * 0.55 + ti_hits * 12 + behavior * 0.25 + len(heuristics) * 5))
    tags = ["T1566"] if score >= 40 else []
    return {
        "score": score,
        "confidence": min(0.95, 0.5 + score / 200),
        "reasons": [Reason(code="COMBINED", message_key="reason.combined")],
        "mitre_tags": tags,
    }
