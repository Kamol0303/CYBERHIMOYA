"""Behavior Analysis Engine (FR-080) — correlate recent defensive signals."""

from __future__ import annotations

from collections import Counter
from typing import Any
from uuid import UUID

from app.services.store import store


def analyze_behavior(user_id: UUID, *, window_limit: int = 50) -> dict[str, Any]:
    scans = store.list_scans(user_id=user_id, limit=window_limit)
    events = store.list_threat_events(user_id, limit=window_limit)
    reasons: list[dict[str, str]] = []
    score = 0
    mitre: set[str] = set()

    malicious_scans = [s for s in scans if s.verdict == "malicious"]
    suspicious_scans = [s for s in scans if s.verdict == "suspicious"]
    critical_events = [e for e in events if e.severity == "critical"]
    warning_events = [e for e in events if e.severity == "warning"]

    if len(malicious_scans) >= 2:
        score += 35
        reasons.append({"code": "MULTI_MALICIOUS", "message_key": "behavior.multi_malicious"})
    elif len(malicious_scans) == 1:
        score += 20
        reasons.append({"code": "RECENT_MALICIOUS", "message_key": "behavior.recent_malicious"})

    if len(suspicious_scans) >= 3:
        score += 20
        reasons.append({"code": "SUSPICIOUS_BURST", "message_key": "behavior.suspicious_burst"})
    elif suspicious_scans:
        score += 8

    if critical_events:
        score += 25
        reasons.append({"code": "CRITICAL_EVENTS", "message_key": "behavior.critical_events"})
    if len(warning_events) >= 2:
        score += 15
        reasons.append({"code": "WARNING_CLUSTER", "message_key": "behavior.warning_cluster"})

    families = Counter(
        (s.meta or {}).get("scam_family")
        for s in scans
        if (s.meta or {}).get("scam_family")
    )
    for family, count in families.items():
        if count >= 2:
            score += 15
            reasons.append(
                {
                    "code": "FAMILY_REPEAT",
                    "message_key": "behavior.family_repeat",
                }
            )
            break

    for s in scans:
        for tag in s.mitre_tags or []:
            mitre.add(tag)
    for e in events:
        for tag in e.mitre_tags or []:
            mitre.add(tag)

    if not reasons:
        reasons.append({"code": "NO_ANOMALY", "message_key": "behavior.clean"})

    score = max(0, min(100, score))
    if score >= 70:
        verdict = "elevated"
        action = "review_activity"
    elif score >= 35:
        verdict = "watch"
        action = "monitor"
    else:
        verdict = "calm"
        action = "none"

    return {
        "score": score,
        "verdict": verdict,
        "confidence": min(0.92, 0.45 + score / 200 + min(len(scans), 20) / 40),
        "recommended_action": action,
        "reasons": reasons,
        "mitre_tags": sorted(mitre),
        "window": {
            "scans": len(scans),
            "threat_events": len(events),
            "malicious_scans": len(malicious_scans),
            "critical_events": len(critical_events),
        },
        "model_version": "behavior-2026.07.1",
        "defensive_only": True,
    }
