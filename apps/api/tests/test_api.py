from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.store import store


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["defensive_only"] is True
    assert "storage" in body


def test_register_login_and_me(client: TestClient):
    r = client.post(
        "/v1/auth/register",
        json={"email": "user@example.com", "password": "securepass1", "locale": "uz"},
    )
    assert r.status_code == 201
    tokens = r.json()
    assert tokens["token_type"] == "Bearer"

    me = client.get("/v1/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "user@example.com"

    login = client.post(
        "/v1/auth/token",
        json={"email": "user@example.com", "password": "securepass1"},
    )
    assert login.status_code == 200


def test_consent_upsert(client: TestClient):
    reg = client.post(
        "/v1/auth/register",
        json={"email": "c@example.com", "password": "securepass1"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post(
        "/v1/consents",
        headers=headers,
        json={"consent_type": "analytics_meta", "granted": True},
    )
    assert r.status_code == 200
    assert r.json()["granted"] is True
    listed = client.get("/v1/consents", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_scan_url_malicious_seed(client: TestClient):
    r = client.post("/v1/scan/url", json={"url": "http://pay-click-uz.tk/login"})
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] in {"malicious", "suspicious"}
    assert body["score"] >= 50
    assert "T1566" in body["mitre_tags"]


def test_scan_url_cleanish(client: TestClient):
    r = client.post("/v1/scan/url", json={"url": "https://example.com/"})
    assert r.status_code == 200
    assert r.json()["score"] < 50


def test_scan_fake_payment_family(client: TestClient):
    r = client.post("/v1/scan/url", json={"url": "https://secure-payme-bonus.xyz/pay"})
    assert r.status_code == 200
    body = r.json()
    assert body["scam_family"] == "payment_scam" or body["score"] >= 40


def test_scan_qr_url(client: TestClient):
    r = client.post(
        "/v1/scan/qr",
        json={"payload_text": "https://gov-subsidy-uz.xyz/claim"},
    )
    assert r.status_code == 200
    assert r.json()["qr_type"] == "url"
    assert r.json()["score"] >= 50


def test_scan_file_hash_hit(client: TestClient):
    r = client.post(
        "/v1/scan/file",
        json={
            "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "file_name": "bank-payme.apk",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] == "malicious"
    assert body["recommended_action"] == "do_not_open"


def test_risk_score(client: TestClient):
    r = client.post(
        "/v1/risk-score",
        json={
            "features": {"url_score": 70, "ti_hits": 2, "behavior_score": 40},
            "subject_type": "url",
        },
    )
    assert r.status_code == 200
    assert 0 <= r.json()["score"] <= 100


def test_threat_feed_sync(client: TestClient):
    r = client.get("/v1/threat-feed/sync")
    assert r.status_code == 200
    body = r.json()
    assert body["item_counts"]["sha256"] >= 1
    assert body["algorithm"] == "ed25519"


def test_erasure_foundation(client: TestClient):
    reg = client.post(
        "/v1/auth/register",
        json={"email": "erase@example.com", "password": "securepass1"},
    )
    token = reg.json()["access_token"]
    assert client.delete("/v1/me", headers={"Authorization": f"Bearer {token}"}).status_code == 202
    assert client.get("/v1/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_scan_history_for_user(client: TestClient):
    reg = client.post(
        "/v1/auth/register",
        json={"email": "hist@example.com", "password": "securepass1"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/v1/scan/url", headers=headers, json={"url": "https://example.com/a"})
    client.post("/v1/scan/url", headers=headers, json={"url": "https://example.com/b"})
    hist = client.get("/v1/scans", headers=headers)
    assert hist.status_code == 200
    assert len(hist.json()) == 2


def test_guest_rate_limit(client: TestClient, monkeypatch):
    monkeypatch.setattr(settings, "guest_rate_limit_per_hour", 2)
    assert client.post("/v1/scan/url", json={"url": "https://example.com/1"}).status_code == 200
    assert client.post("/v1/scan/url", json={"url": "https://example.com/2"}).status_code == 200
    r = client.post("/v1/scan/url", json={"url": "https://example.com/3"})
    assert r.status_code == 429
    assert r.headers["content-type"].startswith("application/problem+json")
    body = r.json()
    assert body["type"] == "https://api.cyberguardian.uz/errors/rate-limited"
    assert body["status"] == 429
    assert body["instance"] == "/v1/scan/url"
    assert r.headers.get("X-RateLimit-Remaining") == "0"


def test_persistence_across_operations(client: TestClient):
    reg = client.post(
        "/v1/auth/register",
        json={"email": "persist@example.com", "password": "securepass1"},
    )
    token = reg.json()["access_token"]
    client.post(
        "/v1/scan/url",
        headers={"Authorization": f"Bearer {token}"},
        json={"url": "https://example.com"},
    )
    assert len(store.list_scans()) >= 1


def test_threat_feed_has_delta_url_and_cdn(client: TestClient):
    r = client.get("/v1/threat-feed/sync")
    assert r.status_code == 200
    body = r.json()
    assert body["delta_url"]
    assert "/cdn/feeds/" in body["delta_url"]
    assert body["algorithm"] == "ed25519"
    version = body["version"]
    cdn = client.get(f"/cdn/feeds/{version}.json")
    assert cdn.status_code == 200
    pack = cdn.json()
    assert pack["signature"] == body["signature"]
    assert pack["algorithm"] == "ed25519"
    assert pack["defensive_only"] is True
    from app.services.feed import verify_signature

    assert verify_signature(pack["signed_payload"], pack["signature"]) is True
    delta = client.get(f"/v1/threat-feed/delta/{version}")
    assert delta.status_code == 200
    verify = client.get("/v1/threat-feed/verify")
    assert verify.status_code == 200
    assert verify.json()["valid"] is True
    pubkey = client.get("/v1/threat-feed/public-key")
    assert pubkey.status_code == 200
    assert pubkey.json()["algorithm"] == "ed25519"


def test_ed25519_reject_tampered_feed():
    from app.services.feed import build_feed_pack, verify_signature

    pack = build_feed_pack("test-tamper")
    assert verify_signature(pack["signed_payload"], pack["signature"]) is True
    assert verify_signature(pack["signed_payload"] + "x", pack["signature"]) is False


def test_create_store_sqlite_factory():
    from app.services.store import SqliteStore, create_store

    s = create_store("sqlite:///:memory:")
    assert isinstance(s, SqliteStore)
    s.create_user("factory@example.com", "securepass1")
    assert s.authenticate("factory@example.com", "securepass1") is not None


def test_emergency_allowlist_pending(client: TestClient):
    r = client.get("/v1/emergency/allowlist")
    assert r.status_code == 200
    body = r.json()
    assert body["aq039_resolved"] is False
    assert body["dry_run_forced"] is True
    assert body["defensive_only"] is True


def test_emergency_allowlist_ignores_replace_placeholders(monkeypatch):
    from app.config import settings
    from app.services import emergency as em

    monkeypatch.setattr(settings, "emergency_sms_allowlist", "REPLACE_WITH_OFFICIAL_SMS_E164")
    monkeypatch.setattr(settings, "emergency_api_allowlist", "PENDING_AQ039")
    monkeypatch.setattr(settings, "emergency_email_allowlist", "")
    monkeypatch.setattr(settings, "emergency_dry_run", False)
    info = em.allowlist_status()
    assert info.aq039_resolved is False
    assert info.dry_run_forced is True


def test_emergency_flow_dry_run(client: TestClient):
    reg = client.post(
        "/v1/auth/register",
        json={"email": "em@example.com", "password": "securepass1"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    denied = client.post(
        "/v1/emergency/confirm",
        headers=headers,
        json={
            "modules": ["url_scan", "file_hash", "sms_local"],
            "confidence": 0.95,
        },
    )
    assert denied.status_code == 403

    assert (
        client.post(
            "/v1/emergency/consent",
            headers=headers,
            json={"granted": True},
        ).status_code
        == 200
    )

    weak = client.post(
        "/v1/emergency/confirm",
        headers=headers,
        json={"modules": ["url_scan"], "confidence": 0.99},
    )
    assert weak.status_code == 422

    conf = client.post(
        "/v1/emergency/confirm",
        headers=headers,
        json={
            "modules": ["url_scan", "file_hash", "sms_local"],
            "confidence": 0.95,
            "incident_ref": "demo-1",
        },
    )
    assert conf.status_code == 200
    confirm_token = conf.json()["confirm_token"]

    disp = client.post(
        "/v1/emergency/dispatch",
        headers=headers,
        json={"confirm_token": confirm_token, "channel": "api"},
    )
    assert disp.status_code == 202
    body = disp.json()
    assert body["dry_run"] is True
    assert body["status"] == "dry_run_logged"
    assert body["evidence_code"].startswith("EV-")

    logs = client.get("/v1/emergency/logs", headers=headers)
    assert logs.status_code == 200
    assert len(logs.json()) == 1


def test_metrics(client: TestClient):
    r = client.get("/v1/metrics")
    assert r.status_code == 200
    body = r.json()
    assert body["defensive_only"] is True
    assert body["version"].startswith("0.")
    assert "feed_version" in body
    assert "scan_rows" in body


def test_scan_file_bad_hash(client: TestClient):
    r = client.post("/v1/scan/file", json={"sha256": "not-a-hash", "file_name": "x.bin"})
    assert r.status_code == 422


def test_security_headers(client: TestClient):
    r = client.get("/health")
    assert r.headers.get("X-CGA-Defensive-Only") == "1"
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("Referrer-Policy") == "no-referrer"
    assert "camera=()" in (r.headers.get("Permissions-Policy") or "")


def test_openapi_has_bearer(client: TestClient):
    r = client.get("/v1/openapi.json")
    assert r.status_code == 200
    schemes = r.json().get("components", {}).get("securitySchemes", {})
    assert "HTTPBearer" in schemes
    assert schemes["HTTPBearer"]["scheme"] == "bearer"


def test_openapi_metrics_schema(client: TestClient):
    r = client.get("/v1/openapi.json")
    assert r.status_code == 200
    schemas = r.json().get("components", {}).get("schemas", {})
    assert "MetricsResponse" in schemas
    props = schemas["MetricsResponse"]["properties"]
    for key in (
        "version",
        "environment",
        "defensive_only",
        "emergency_dry_run",
        "scan_rows",
        "feed_version",
    ):
        assert key in props


def test_unauthorized_problem_detail(client: TestClient):
    r = client.get("/v1/me")
    assert r.status_code == 401
    assert r.headers["content-type"].startswith("application/problem+json")
    body = r.json()
    assert body["type"] == "https://api.cyberguardian.uz/errors/unauthorized"
    assert body["status"] == 401
    assert body["instance"] == "/v1/me"


def test_cors_web_origin_preflight(client: TestClient):
    origin = "http://localhost:5173"
    r = client.options(
        "/v1/scan/url",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.status_code in {200, 204}
    assert r.headers.get("access-control-allow-origin") == origin


def test_cors_chrome_extension_preflight(client: TestClient):
    # Unpacked extension IDs are 32 lowercase letters (a-p typically).
    origin = "chrome-extension://abcdefghijklmnopqrstuvwxyzabcdef"
    r = client.options(
        "/v1/scan/url",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.status_code in {200, 204}
    assert r.headers.get("access-control-allow-origin") == origin


def test_parse_cors_origins_chrome_wildcard():
    from app.cors_util import parse_cors_origins

    exact, regex = parse_cors_origins(
        "http://localhost:5173,chrome-extension://*,http://127.0.0.1:5173"
    )
    assert exact == ["http://localhost:5173", "http://127.0.0.1:5173"]
    assert regex is not None
    assert "chrome-extension://" in regex


def test_suspicious_message_job_scam(client: TestClient):
    r = client.post(
        "/v1/messages/suspicious",
        json={
            "text": "Kuniga 500$ ish — yozing @example_bot",
            "source": "paste",
            "entities": {"urls": [], "bot_username": "example_bot"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["score"] >= 50
    assert body["scam_family"] == "telegram_job_scam"
    assert body["campaign_id"]
    assert "preview" in body


def test_breach_check_seed_and_clean(client: TestClient):
    hit = client.post("/v1/breach-check", json={"email": "breach@example.com"})
    assert hit.status_code == 200
    assert hit.json()["found"] is True
    assert hit.json()["breach_count"] >= 1
    assert "change_password" in hit.json()["recommendations"]
    clean = client.post("/v1/breach-check", json={"email": "nobody-clean@example.com"})
    assert clean.status_code == 200
    assert clean.json()["found"] is False


def test_devices_register_list_delete(client: TestClient):
    reg = client.post(
        "/v1/auth/register",
        json={"email": "device@example.com", "password": "securepass1"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/v1/devices/register",
        headers=headers,
        json={"platform": "web", "app_version": "0.3.0", "fingerprint": "fp-test-1"},
    )
    assert created.status_code == 200
    listed = client.get("/v1/devices", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 1
    device_id = created.json()["id"]
    assert client.delete(f"/v1/devices/{device_id}", headers=headers).status_code == 204
    assert client.get("/v1/devices", headers=headers).json() == []


def test_scan_url_hunting_metadata(client: TestClient):
    r1 = client.post("/v1/scan/url", json={"url": "http://pay-click-uz.tk/login"})
    r2 = client.post("/v1/scan/url", json={"url": "http://pay-click-uz.tk/login"})
    assert r1.status_code == 200 and r2.status_code == 200
    b1, b2 = r1.json(), r2.json()
    assert b1["intent_tags"]
    assert b1["campaign_id"]
    assert b1["campaign_id"] == b2["campaign_id"]
    assert b1["kill_chain_stage"] == "delivery"


def test_scan_qr_payment_hunting_metadata(client: TestClient):
    r = client.post("/v1/scan/qr", json={"payload_text": "payme sum=100000"})
    assert r.status_code == 200
    body = r.json()
    assert body["qr_type"] == "payment"
    assert body["intent_tags"]
    assert body["campaign_id"]


def test_file_yara_stub(client: TestClient):
    r = client.post(
        "/v1/scan/file",
        json={
            "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
            "file_name": "click-wallet.apk",
            "run_yara": True,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert any(m["rule"] == "stub_apk_lure" for m in body["yara_matches"])


def test_threat_events_and_notifications(client: TestClient):
    reg = client.post(
        "/v1/auth/register",
        json={"email": "threat@example.com", "password": "securepass1"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    assert client.post(
        "/v1/scan/url", headers=headers, json={"url": "http://pay-click-uz.tk/x"}
    ).status_code == 200
    events = client.get("/v1/threat-events", headers=headers)
    assert events.status_code == 200
    assert len(events.json()) >= 1
    assert events.json()[0]["severity"] in {"warning", "critical"}
    notifs = client.get("/v1/notifications", headers=headers)
    assert notifs.status_code == 200
    assert len(notifs.json()) >= 1
    nid = notifs.json()[0]["id"]
    marked = client.post(f"/v1/notifications/{nid}/read", headers=headers)
    assert marked.status_code == 200
    assert marked.json()["read_at"] is not None


def test_report_export(client: TestClient):
    reg = client.post(
        "/v1/auth/register",
        json={"email": "report@example.com", "password": "securepass1"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    client.post("/v1/scan/url", headers=headers, json={"url": "https://example.com/"})
    r = client.post(
        "/v1/reports",
        headers=headers,
        json={
            "from": "2020-01-01T00:00:00Z",
            "to": "2030-01-01T00:00:00Z",
            "types": ["scan", "threat_event"],
            "format": "json",
            "redact_pii": True,
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "ready"
    assert "sections" in body["payload"]
    got = client.get(f"/v1/reports/{body['report_id']}", headers=headers)
    assert got.status_code == 200


def test_password_health_and_scan_detail(client: TestClient):
    weak = client.post("/v1/password-health", json={"password": "123456"})
    assert weak.status_code == 200
    assert weak.json()["verdict"] == "weak"
    strong = client.post("/v1/password-health", json={"password": "Tr0ub4dor&3-long!"})
    assert strong.status_code == 200
    assert strong.json()["score"] >= 50

    reg = client.post(
        "/v1/auth/register",
        json={"email": "detail@example.com", "password": "securepass1"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    scan = client.post(
        "/v1/scan/url", headers=headers, json={"url": "https://example.com/detail"}
    )
    scan_id = scan.json()["scan_id"]
    detail = client.get(f"/v1/scans/{scan_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["scan_id"] == scan_id
    assert "reasons" in detail.json()

    hist = client.get("/v1/risk-score/history", headers=headers)
    assert hist.status_code == 200
    assert len(hist.json()) >= 1
    assert hist.json()[0]["score"] == scan.json()["score"]

    scored = client.post(
        "/v1/risk-score",
        headers=headers,
        json={"features": {"url_score": 70, "ti_hits": 1}, "subject_type": "url"},
    )
    assert scored.status_code == 200
    hist2 = client.get("/v1/risk-score/history", headers=headers)
    assert len(hist2.json()) >= 2
