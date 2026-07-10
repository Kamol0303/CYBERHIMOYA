"""Offline email breach check (FR-051) — hash lookup only, no plaintext logs."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.store_models import hash_email

SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "breaches" / "seed.json"

RECOMMENDATIONS = ["change_password", "enable_2fa", "unique_passwords"]


def _load_seed() -> dict[str, list[dict]]:
    if not SEED_PATH.is_file():
        return {}
    raw = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    out: dict[str, list[dict]] = {}
    for row in raw.get("entries", []):
        email = row.get("email")
        if not email:
            continue
        digest = hash_email(email)
        out[digest] = row.get("breaches") or []
    return out


_SEED = _load_seed()


def check_email(email: str) -> dict:
    digest = hash_email(email)
    breaches = _SEED.get(digest, [])
    found = len(breaches) > 0
    return {
        "found": found,
        "breach_count": len(breaches),
        "breaches": breaches,
        "recommendations": list(RECOMMENDATIONS) if found else [],
        "email_hash_prefix": digest[:12],
    }
