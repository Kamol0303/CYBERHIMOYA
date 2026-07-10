from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timezone

from app.config import settings
from app.models.schemas import ThreatFeedSyncResponse
from app.services.scoring import KNOWN_MALICIOUS_DOMAINS

# Stub signed delta — clients must verify signature before apply (NFR-011).
FEED_ITEMS = [
    {"kind": "domain", "value": d, "severity": "malicious", "family": "seed_ioc"}
    for d in sorted(KNOWN_MALICIOUS_DOMAINS)
] + [
    {"kind": "domain", "value": "payme.uz", "severity": "trusted", "family": "payment_legit"},
    {"kind": "domain", "value": "click.uz", "severity": "trusted", "family": "payment_legit"},
    {"kind": "domain", "value": "my.gov.uz", "severity": "trusted", "family": "gov_legit"},
]


def _sign(payload: str) -> str:
    digest = hashlib.sha256((settings.secret_key + payload).encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def sync_feed(since_version: str | None = None) -> ThreatFeedSyncResponse:
    version = settings.feed_version
    payload = f"{version}|{len(FEED_ITEMS)}"
    items = FEED_ITEMS if since_version != version else []
    counts = {"url": 0, "domain": 0, "sha256": 0}
    for item in FEED_ITEMS:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1
    return ThreatFeedSyncResponse(
        version=version,
        generated_at=datetime.now(timezone.utc),
        delta_url=None,
        signature=_sign(payload),
        algorithm="ed25519-stub",
        item_counts=counts,
        items=items,
    )
