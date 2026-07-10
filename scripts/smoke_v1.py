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

from app.main import app  # noqa: E402


def main() -> int:
    client = TestClient(app)
    checks: list[tuple[str, bool]] = []

    def ok(name: str, cond: bool) -> None:
        checks.append((name, cond))
        print(("PASS" if cond else "FAIL"), name)

    r = client.get("/health")
    ok("health", r.status_code == 200 and r.json().get("defensive_only") is True)
    ok("version", r.json().get("version", "").startswith("0."))

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
    ok(
        "emergency_dispatch_dry_run",
        disp.status_code == 202 and disp.json().get("dry_run") is True,
    )

    failed = [n for n, c in checks if not c]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
