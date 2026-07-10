from __future__ import annotations

import re
from hashlib import sha256
from typing import Any
from urllib.parse import urlparse
from uuid import UUID, uuid4

from app.models.schemas import (
    FileScanResponse,
    QrScanResponse,
    Reason,
    UrlScanResponse,
    Verdict,
)
from app.services.store import store
from app.services.store_models import ScanRow, utcnow
from app.services.hunting import attach_hunting

# Seed IOC / heuristic lists — defensive reputation only (no active probing).
KNOWN_MALICIOUS_DOMAINS = {
    "pay-click-uz.tk",
    "gov-subsidy-uz.xyz",
    "telegram-bonus-uz.ml",
    "iiv-fine-pay.ru.com",
    "click-payme-secure.cf",
}

KNOWN_MALICIOUS_SHA256 = {
    # Synthetic seed hashes for V1 demos (not real malware samples).
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa": {
        "tag": "apk.banker.seed",
        "family": "fake_bank_apk",
    },
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb": {
        "tag": "apk.dropper.seed",
        "family": "trojan_dropper_seed",
    },
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


def _verdict_from_score(score: int) -> tuple[Verdict, str, float]:
    if score >= 80:
        return Verdict.malicious, "block_and_warn", 0.88
    if score >= 50:
        return Verdict.suspicious, "warn_and_review", 0.72
    if score >= 20:
        return Verdict.suspicious, "caution", 0.55
    return Verdict.clean, "allow", 0.6


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
    verdict, action, confidence = _verdict_from_score(score)
    if verdict == Verdict.clean and not reasons:
        reasons.append(Reason(code="NO_TI_HIT", message_key="reason.no_ti_hit"))

    payload = {
        "url_normalized": normalized,
        "score": score,
        "confidence": confidence,
        "verdict": verdict,
        "reasons": reasons,
        "mitre_tags": sorted(set(mitre)),
        "scam_family": scam_family,
        "actor_hint": actor_hint,
        "recommended_action": action,
        "subject_hash": _subject_hash(normalized),
    }
    return attach_hunting(payload, subject_key=domain)


def classify_qr_payload(payload_text: str) -> str:
    text = payload_text.strip()
    if re.match(r"^https?://", text, re.I) or "." in text.split()[0]:
        return "url"
    if any(k in text.lower() for k in ("payme", "click", "uzcard", "humo", "sum=")):
        return "payment"
    if text:
        return "text"
    return "unknown"


def scan_url(url: str, user_id: UUID | None = None) -> UrlScanResponse:
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
                "intent_tags": result.get("intent_tags", []),
                "campaign_id": result.get("campaign_id"),
                "kill_chain_stage": result.get("kill_chain_stage"),
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
        intent_tags=result.get("intent_tags", []),
        campaign_id=result.get("campaign_id"),
        kill_chain_stage=result.get("kill_chain_stage"),
        scanned_at=utcnow(),
    )


def scan_qr(payload_text: str, user_id: UUID | None = None) -> QrScanResponse:
    qr_type = classify_qr_payload(payload_text)
    if qr_type == "url":
        result = score_url(payload_text)
        scan_id = uuid4()
        store.add_scan(
            ScanRow(
                id=scan_id,
                user_id=user_id,
                scan_type="qr",
                score=result["score"],
                verdict=result["verdict"].value,
                reasons=[r.model_dump() for r in result["reasons"]],
                subject_hash=result["subject_hash"],
                mitre_tags=result["mitre_tags"],
                meta={
                    "qr_type": qr_type,
                    "scam_family": result["scam_family"],
                    "actor_hint": result["actor_hint"],
                    "recommended_action": result["recommended_action"],
                    "intent_tags": result.get("intent_tags", []),
                    "campaign_id": result.get("campaign_id"),
                    "kill_chain_stage": result.get("kill_chain_stage"),
                },
                created_at=utcnow(),
            )
        )
        return QrScanResponse(
            scan_id=scan_id,
            qr_type=qr_type,
            payload_preview=payload_text[:200],
            url_normalized=result["url_normalized"],
            score=result["score"],
            confidence=result["confidence"],
            verdict=result["verdict"],
            reasons=result["reasons"],
            mitre_tags=result["mitre_tags"],
            scam_family=result["scam_family"],
            actor_hint=result["actor_hint"],
            recommended_action=result["recommended_action"],
            intent_tags=result.get("intent_tags", []),
            campaign_id=result.get("campaign_id"),
            kill_chain_stage=result.get("kill_chain_stage"),
            scanned_at=utcnow(),
        )

    reasons = [Reason(code="QR_NON_URL", message_key="reason.qr_non_url")]
    score = 25 if qr_type == "payment" else 10
    if qr_type == "payment":
        reasons.append(Reason(code="QR_PAYMENT_PAYLOAD", message_key="reason.qr_payment"))
    verdict, action, confidence = _verdict_from_score(score)
    scan_id = uuid4()
    subject = sha256(payload_text.encode("utf-8")).hexdigest()
    mitre = ["T1566"] if qr_type == "payment" else []
    family = SCAM_FAMILY_PAYMENT if qr_type == "payment" else None
    hunting = attach_hunting(
        {
            "score": score,
            "scam_family": family,
            "reasons": reasons,
            "mitre_tags": mitre,
        },
        subject_key=subject[:16],
    )
    store.add_scan(
        ScanRow(
            id=scan_id,
            user_id=user_id,
            scan_type="qr",
            score=score,
            verdict=verdict.value,
            reasons=[r.model_dump() for r in reasons],
            subject_hash=subject,
            mitre_tags=mitre,
            meta={
                "qr_type": qr_type,
                "recommended_action": action,
                "scam_family": family,
                "intent_tags": hunting["intent_tags"],
                "campaign_id": hunting["campaign_id"],
                "kill_chain_stage": hunting["kill_chain_stage"],
            },
            created_at=utcnow(),
        )
    )
    return QrScanResponse(
        scan_id=scan_id,
        qr_type=qr_type,
        payload_preview=payload_text[:200],
        url_normalized=None,
        score=score,
        confidence=confidence,
        verdict=verdict,
        reasons=reasons,
        mitre_tags=mitre,
        scam_family=family,
        actor_hint=None,
        recommended_action=action,
        intent_tags=hunting["intent_tags"],
        campaign_id=hunting["campaign_id"],
        kill_chain_stage=hunting["kill_chain_stage"],
        scanned_at=utcnow(),
    )


def scan_file_hash(
    sha256_hex: str,
    file_name: str | None = None,
    user_id: UUID | None = None,
    run_yara: bool = False,
) -> FileScanResponse:
    digest = sha256_hex.strip().lower()
    if not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ValueError("invalid_sha256")

    reasons: list[Reason] = []
    mitre: list[str] = []
    ti_hits: list[dict[str, str]] = []
    yara_matches: list[dict[str, str]] = []
    score = 5
    scam_family: str | None = None

    hit = KNOWN_MALICIOUS_SHA256.get(digest)
    if hit:
        score += 85
        reasons.append(Reason(code="TI_HASH_HIT", message_key="reason.ti_hash_hit"))
        ti_hits.append({"source": "internal", "tag": hit["tag"]})
        scam_family = hit["family"]
        mitre.append("T1204")

    name = (file_name or "").lower()
    if name.endswith(".apk") and ("bank" in name or "payme" in name or "click" in name):
        score += 20
        reasons.append(Reason(code="APK_NAME_HEURISTIC", message_key="reason.apk_name"))
        scam_family = scam_family or "fake_bank_apk"
        mitre.append("T1204")

    # Lightweight stub — no yara-python dependency in V1.
    if run_yara:
        if name.endswith(".apk") and any(k in name for k in ("bank", "payme", "click", "wallet")):
            yara_matches.append({"rule": "stub_apk_lure", "namespace": "cga-stub"})
            score += 10
            reasons.append(Reason(code="YARA_STUB_HIT", message_key="reason.yara_stub"))
        else:
            reasons.append(Reason(code="YARA_STUB_EMPTY", message_key="reason.yara_stub_empty"))

    score = max(0, min(100, score))
    verdict, action, confidence = _verdict_from_score(score)
    if verdict == Verdict.clean and not reasons:
        reasons.append(Reason(code="NO_TI_HIT", message_key="reason.no_ti_hit"))
        action = "allow"

    if verdict == Verdict.malicious:
        action = "do_not_open"

    hunting = attach_hunting(
        {
            "score": score,
            "scam_family": scam_family,
            "reasons": reasons,
            "mitre_tags": sorted(set(mitre)),
        },
        subject_key=digest[:16],
    )
    scan_id = uuid4()
    store.add_scan(
        ScanRow(
            id=scan_id,
            user_id=user_id,
            scan_type="file",
            score=score,
            verdict=verdict.value,
            reasons=[r.model_dump() for r in reasons],
            subject_hash=digest,
            mitre_tags=sorted(set(mitre)),
            meta={
                "file_name": file_name,
                "scam_family": scam_family,
                "recommended_action": action,
                "ti_hits": ti_hits,
                "yara_matches": yara_matches,
                "intent_tags": hunting["intent_tags"],
                "campaign_id": hunting["campaign_id"],
                "kill_chain_stage": hunting["kill_chain_stage"],
            },
            created_at=utcnow(),
        )
    )
    return FileScanResponse(
        scan_id=scan_id,
        sha256=digest,
        file_name=file_name,
        score=score,
        confidence=confidence,
        verdict=verdict,
        ti_hits=ti_hits,
        yara_matches=yara_matches,
        reasons=reasons,
        mitre_tags=sorted(set(mitre)),
        scam_family=scam_family,
        actor_hint="uz_apk_seed" if scam_family else None,
        recommended_action=action,
        intent_tags=hunting["intent_tags"],
        campaign_id=hunting["campaign_id"],
        kill_chain_stage=hunting["kill_chain_stage"],
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
