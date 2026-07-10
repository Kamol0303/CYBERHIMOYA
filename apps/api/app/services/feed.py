from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings
from app.models.schemas import ThreatFeedSyncResponse
from app.services.feed_crypto import public_key_b64, sign_ed25519, verify_ed25519
from app.services.scoring import KNOWN_MALICIOUS_DOMAINS, KNOWN_MALICIOUS_SHA256

FEEDS_DIR = Path(__file__).resolve().parent.parent / "data" / "feeds"
ALGORITHM = "ed25519"

FEED_ITEMS: list[dict[str, Any]] = [
    {"kind": "domain", "value": d, "severity": "malicious", "family": "seed_ioc"}
    for d in sorted(KNOWN_MALICIOUS_DOMAINS)
] + [
    {
        "kind": "sha256",
        "value": digest,
        "severity": "malicious",
        "family": meta["family"],
    }
    for digest, meta in sorted(KNOWN_MALICIOUS_SHA256.items())
] + [
    {"kind": "domain", "value": "payme.uz", "severity": "trusted", "family": "payment_legit"},
    {"kind": "domain", "value": "click.uz", "severity": "trusted", "family": "payment_legit"},
    {"kind": "domain", "value": "my.gov.uz", "severity": "trusted", "family": "gov_legit"},
]


def canonical_payload(version: str, items: list[dict[str, Any]]) -> str:
    canonical = json.dumps(items, sort_keys=True, separators=(",", ":"))
    return f"{version}|{canonical}"


def sign_payload(payload: str) -> str:
    return sign_ed25519(payload)


def verify_signature(payload: str, signature: str) -> bool:
    return verify_ed25519(payload, signature)


def build_feed_pack(version: str | None = None) -> dict[str, Any]:
    ver = version or settings.feed_version
    counts = {"url": 0, "domain": 0, "sha256": 0}
    for item in FEED_ITEMS:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1
    payload = canonical_payload(ver, FEED_ITEMS)
    body = {
        "version": ver,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "algorithm": ALGORITHM,
        "public_key_b64": public_key_b64(),
        "item_counts": counts,
        "items": FEED_ITEMS,
        "defensive_only": True,
        "signed_payload": payload,
        "signature": sign_payload(payload),
    }
    return body


def ensure_feed_files(version: str | None = None) -> Path:
    """Write signed feed JSON under app/data/feeds for CDN serving."""
    ver = version or settings.feed_version
    FEEDS_DIR.mkdir(parents=True, exist_ok=True)
    pack = build_feed_pack(ver)
    path = FEEDS_DIR / f"{ver}.json"
    path.write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (FEEDS_DIR / f"{ver}.sig").write_text(pack["signature"] + "\n", encoding="utf-8")
    return path


def load_feed_pack(version: str | None = None) -> dict[str, Any]:
    ver = version or settings.feed_version
    path = FEEDS_DIR / f"{ver}.json"
    if not path.exists():
        ensure_feed_files(ver)
        return json.loads(path.read_text(encoding="utf-8"))
    pack = json.loads(path.read_text(encoding="utf-8"))
    # Re-sign if algorithm upgraded or signature invalid for current keys.
    if pack.get("algorithm") != ALGORITHM or not verify_signature(
        pack.get("signed_payload", ""), pack.get("signature", "")
    ):
        ensure_feed_files(ver)
        pack = json.loads(path.read_text(encoding="utf-8"))
    return pack


def sync_feed(since_version: str | None = None) -> ThreatFeedSyncResponse:
    pack = load_feed_pack()
    version = pack["version"]
    items = pack["items"] if since_version != version else []
    delta_url = f"{settings.public_base_url.rstrip('/')}/cdn/feeds/{version}.json"
    return ThreatFeedSyncResponse(
        version=version,
        generated_at=datetime.fromisoformat(pack["generated_at"].replace("Z", "+00:00")),
        delta_url=delta_url,
        signature=pack["signature"],
        algorithm=pack.get("algorithm", ALGORITHM),
        item_counts=pack["item_counts"],
        items=items,
    )
