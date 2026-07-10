#!/usr/bin/env python3
"""V1 defensive smoke checks (in-process TestClient — no live server required)."""

from __future__ import annotations

import os
import sys

os.environ.setdefault("CGA_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("CGA_GUEST_RATE_LIMIT_PER_HOUR", "1000")

ROOT = os.path.join(os.path.dirname(__file__), "..", "apps", "api")
sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient  # noqa: E402

from app import __version__  # noqa: E402
from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from app.services.rate_limit import guest_limiter  # noqa: E402


def main() -> int:
    client = TestClient(app)
    checks: list[tuple[str, bool]] = []

    def ok(name: str, cond: bool) -> None:
        checks.append((name, cond))
        print(("PASS" if cond else "FAIL"), name)

    r = client.get("/health")
    ok("health", r.status_code == 200 and r.json().get("defensive_only") is True)
    ok("version", r.json().get("version") == __version__)

    r = client.post("/v1/scan/url", json={"url": "http://pay-click-uz.tk/x"})
    ok("scan_url_malicious", r.status_code == 200 and r.json()["score"] >= 50)
    ok("rate_limit_headers", "X-RateLimit-Limit" in r.headers)

    r = client.post(
        "/v1/scan/file",
        json={
            "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "file_name": "bank.apk",
        },
    )
    ok("scan_file_seed", r.status_code == 200 and r.json()["verdict"] == "malicious")

    r = client.get("/v1/threat-feed/sync")
    ok("feed_ed25519", r.status_code == 200 and r.json().get("algorithm") == "ed25519")

    r = client.get("/v1/emergency/allowlist")
    ok("emergency_dry_run", r.status_code == 200 and r.json().get("dry_run_forced") is True)

    reg = client.post(
        "/v1/auth/register",
        json={"email": "smoke@example.com", "password": "securepass1", "locale": "uz"},
    )
    ok("auth_register", reg.status_code == 201)
    token = reg.json().get("access_token", "")
    headers = {"Authorization": f"Bearer {token}"}
    dev = client.post(
        "/v1/devices/register",
        headers=headers,
        json={"platform": "web", "app_version": "0.3.0", "fingerprint": "smoke-fp"},
    )
    ok("device_register", dev.status_code == 200)
    listed = client.get("/v1/devices", headers=headers)
    ok("device_list", listed.status_code == 200 and len(listed.json()) >= 1)
    client.post("/v1/emergency/consent", headers=headers, json={"granted": True})
    conf = client.post(
        "/v1/emergency/confirm",
        headers=headers,
        json={"modules": ["url_scan", "file_hash", "sms_local"], "confidence": 0.95},
    )
    ok("emergency_confirm", conf.status_code == 200)
    disp = client.post(
        "/v1/emergency/dispatch",
        headers=headers,
        json={"confirm_token": conf.json()["confirm_token"], "channel": "api"},
    )
    ok("emergency_dispatch_dry_run", disp.status_code == 202 and disp.json().get("dry_run") is True)

    r = client.get("/v1/threat-feed/verify")
    ok("feed_verify", r.status_code == 200 and r.json().get("valid") is True)

    ver = client.get("/v1/threat-feed/sync").json().get("version", "20260710.2")
    cdn = client.get(f"/cdn/feeds/{ver}.json")
    ok("feed_cdn", cdn.status_code == 200 and "signature" in cdn.json())

    r = client.get("/v1/metrics")
    ok(
        "metrics",
        r.status_code == 200
        and r.json().get("defensive_only") is True
        and r.json().get("version") == __version__,
    )

    r = client.get("/health")
    ok("security_header", r.headers.get("X-CGA-Defensive-Only") == "1")
    ok("security_frame", r.headers.get("X-Frame-Options") == "DENY")

    r = client.get("/v1/me")
    ok("auth_401", r.status_code == 401)
    body401 = r.json() if r.status_code == 401 else {}
    ok(
        "auth_401_problem",
        r.headers.get("content-type", "").startswith("application/problem+json")
        and body401.get("type") == "https://api.cyberguardian.uz/errors/unauthorized"
        and body401.get("status") == 401
        and body401.get("instance") == "/v1/me",
    )

    guest_limiter.reset()
    prev_limit = settings.guest_rate_limit_per_hour
    settings.guest_rate_limit_per_hour = 2
    try:
        client.post("/v1/scan/url", json={"url": "https://example.com/smoke-1"})
        client.post("/v1/scan/url", json={"url": "https://example.com/smoke-2"})
        r = client.post("/v1/scan/url", json={"url": "https://example.com/smoke-3"})
        ok("guest_rate_limit_429", r.status_code == 429)
        body = r.json() if r.status_code == 429 else {}
        ok(
            "guest_rate_limit_problem",
            body.get("type") == "https://api.cyberguardian.uz/errors/rate-limited"
            and body.get("status") == 429
            and r.headers.get("X-RateLimit-Remaining") == "0",
        )
    finally:
        settings.guest_rate_limit_per_hour = prev_limit
        guest_limiter.reset()

    r = client.post(
        "/v1/messages/suspicious",
        json={"text": "Kuniga 500$ ish @job_bot", "source": "paste"},
    )
    ok("message_suspicious", r.status_code == 200 and r.json().get("score", 0) >= 50)

    r = client.post("/v1/breach-check", json={"email": "smoke@example.com"})
    ok("breach_seed", r.status_code == 200 and r.json().get("found") is True)

    r = client.post("/v1/scan/url", json={"url": "http://pay-click-uz.tk/x"})
    ok(
        "hunting_meta",
        r.status_code == 200
        and bool(r.json().get("intent_tags"))
        and bool(r.json().get("campaign_id")),
    )

    # Authenticated threat event + notification
    auth_scan = client.post(
        "/v1/scan/url",
        headers=headers,
        json={"url": "http://gov-subsidy-uz.xyz/claim"},
    )
    ok("auth_scan", auth_scan.status_code == 200)
    ev = client.get("/v1/threat-events", headers=headers)
    ok("threat_events", ev.status_code == 200 and len(ev.json()) >= 1)
    nf = client.get("/v1/notifications", headers=headers)
    ok("notifications", nf.status_code == 200 and len(nf.json()) >= 1)
    rh = client.get("/v1/risk-score/history", headers=headers)
    ok("risk_history", rh.status_code == 200 and len(rh.json()) >= 1)
    pwd = client.post("/v1/password-health", json={"password": "not-a-secret-demo"})
    ok("password_health", pwd.status_code == 200 and "verdict" in pwd.json())

    failed = [n for n, c in checks if not c]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
