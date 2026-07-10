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
    assert client.post("/v1/scan/url", json={"url": "https://example.com/3"}).status_code == 429


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


def test_security_headers(client: TestClient):
    r = client.get("/health")
    assert r.headers.get("X-CGA-Defensive-Only") == "1"
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
