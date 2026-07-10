"""Sigma rule catalog stub (FR-081) — metadata only, no offensive payloads."""

from __future__ import annotations

from typing import Any

# Versioned defensive detection rules (titles + MITRE only).
SIGMA_RULES: list[dict[str, Any]] = [
    {
        "id": "cga-sigma-001",
        "title": "Suspicious short-TLD domain in URL scan",
        "version": "2026.07.1",
        "status": "stable",
        "mitre_tags": ["T1566"],
        "platforms": ["web", "extension", "api"],
        "defensive_only": True,
    },
    {
        "id": "cga-sigma-002",
        "title": "Payment scam keyword cluster",
        "version": "2026.07.1",
        "status": "stable",
        "mitre_tags": ["T1566.002"],
        "platforms": ["web", "android", "api"],
        "defensive_only": True,
    },
    {
        "id": "cga-sigma-003",
        "title": "Gov impersonation lure",
        "version": "2026.07.1",
        "status": "stable",
        "mitre_tags": ["T1566", "T1598"],
        "platforms": ["web", "android", "api"],
        "defensive_only": True,
    },
    {
        "id": "cga-sigma-004",
        "title": "Unsigned / heuristic process name (Windows stub)",
        "version": "2026.07.1",
        "status": "experimental",
        "mitre_tags": ["T1059"],
        "platforms": ["windows"],
        "defensive_only": True,
    },
]


def list_sigma_rules() -> list[dict[str, Any]]:
    return list(SIGMA_RULES)
