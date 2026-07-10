"""DNS / domain reputation helpers (FR-060) — defensive warn only."""

from __future__ import annotations

from urllib.parse import urlparse

from app.services.scoring import KNOWN_MALICIOUS_DOMAINS, KNOWN_SUSPICIOUS_TLDS


def normalize_domain(raw: str) -> str:
    value = raw.strip().lower()
    if "://" in value:
        host = urlparse(value).hostname or ""
    else:
        host = value.split("/")[0].split("?")[0]
    host = host.rstrip(".").removeprefix("www.")
    if not host or "." not in host or " " in host:
        raise ValueError("invalid_domain")
    return host


def assess_domain(domain: str, *, allowlisted: bool) -> dict:
    if allowlisted:
        return {
            "domain": domain,
            "verdict": "clean",
            "score": 0,
            "allowlisted": True,
            "recommended_action": "allow",
            "reasons": [{"code": "ALLOWLIST", "message_key": "dns.allowlisted"}],
        }
    if domain in KNOWN_MALICIOUS_DOMAINS or any(
        domain.endswith("." + d) for d in KNOWN_MALICIOUS_DOMAINS
    ):
        return {
            "domain": domain,
            "verdict": "malicious",
            "score": 95,
            "allowlisted": False,
            "recommended_action": "block_and_warn",
            "reasons": [{"code": "IOC_DOMAIN", "message_key": "dns.malicious"}],
        }
    tld_hit = any(domain.endswith(tld) for tld in KNOWN_SUSPICIOUS_TLDS)
    if tld_hit:
        return {
            "domain": domain,
            "verdict": "suspicious",
            "score": 55,
            "allowlisted": False,
            "recommended_action": "warn_and_review",
            "reasons": [{"code": "SUSPICIOUS_TLD", "message_key": "dns.suspicious_tld"}],
        }
    return {
        "domain": domain,
        "verdict": "clean",
        "score": 5,
        "allowlisted": False,
        "recommended_action": "allow",
        "reasons": [{"code": "NO_HIT", "message_key": "dns.clean"}],
    }
