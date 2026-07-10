from __future__ import annotations

import base64
import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings
from app.models.schemas import ThreatFeedSyncResponse
from app.services.scoring import KNOWN_MALICIOUS_DOMAINS, KNOWN_MALICIOUS_SHA256

FEEDS_DIR = Path(__file__).resolve().parent.parent / "data" / "feeds"

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


def sign_payload(payload: str, secret: str | None = None) -> str:
    key = secret if secret is not None else settings.secret_key
    digest = hashlib.sha256((key + payload).encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def verify_signature(payload: str, signature: str, secret: str | None = None) -> bool:
    expected = sign_payload(payload, secret)
    return secrets.compare_digest(expected, signature)


def build_feed_pack(version: str | None = None) -> dict[str, Any]:
    ver = version or settings.feed_version
    counts = {"url": 0, "domain": 0, "sha256": 0}
    for item in FEED_ITEMS:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1
    body = {
        "version": ver,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "algorithm": "ed25519-stub",
        "item_counts": counts,
        "items": FEED_ITEMS,
        "defensive_only": True,
    }
    canonical = json.dumps(body["items"], sort_keys=True, separators=(",", ":"))
    payload = f"{ver}|{canonical}"
    body["signature"] = sign_payload(payload)
    body["signed_payload"] = payload
    return body


def ensure_feed_files(version: str | None = None) -> Path:
    """Write signed feed JSON under app/data/feeds for CDN serving."""
    ver = version or settings.feed_version
    FEEDS_DIR.mkdir(parents=True, exist_ok=True)
    pack = build_feed_pack(ver)
    path = FEEDS_DIR / f"{ver}.json"
    path.write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sig_path = FEEDS_DIR / f"{ver}.sig"
    sig_path.write_text(pack["signature"] + "\n", encoding="utf-8")
    return path


def load_feed_pack(version: str | None = None) -> dict[str, Any]:
    ver = version or settings.feed_version
    path = FEEDS_DIR / f"{ver}.json"
    if not path.exists():
        ensure_feed_files(ver)
    return json.loads(path.read_text(encoding="utf-8"))


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
        algorithm=pack.get("algorithm", "ed25519-stub"),
        item_counts=pack["item_counts"],
        items=items,
    )
