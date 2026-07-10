from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.store import store


@pytest.fixture(autouse=True)
def reset_store():
    store.users.clear()
    store.users_by_email_hash.clear()
    store.consents.clear()
    store.scans.clear()
    store.audits.clear()
    store.refresh_tokens.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["defensive_only"] is True


def test_register_login_and_me(client: TestClient):
    r = client.post(
        "/v1/auth/register",
        json={"email": "user@example.com", "password": "securepass1", "locale": "uz"},
    )
    assert r.status_code == 201
    tokens = r.json()
    assert tokens["token_type"] == "Bearer"
    assert "access_token" in tokens

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
    assert body["recommended_action"] in {"block_and_warn", "warn_and_review", "caution"}


def test_scan_url_cleanish(client: TestClient):
    r = client.post("/v1/scan/url", json={"url": "https://example.com/"})
    assert r.status_code == 200
    body = r.json()
    assert body["score"] < 50
    assert body["verdict"] in {"clean", "suspicious", "unknown"}


def test_scan_fake_payment_family(client: TestClient):
    r = client.post("/v1/scan/url", json={"url": "https://secure-payme-bonus.xyz/pay"})
    assert r.status_code == 200
    body = r.json()
    assert body["scam_family"] == "payment_scam" or body["score"] >= 40


def test_risk_score(client: TestClient):
    r = client.post(
        "/v1/risk-score",
        json={
            "features": {"url_score": 70, "ti_hits": 2, "behavior_score": 40, "local_heuristics": ["punycode"]},
            "subject_type": "url",
        },
    )
    assert r.status_code == 200
    assert 0 <= r.json()["score"] <= 100


def test_threat_feed_sync(client: TestClient):
    r = client.get("/v1/threat-feed/sync")
    assert r.status_code == 200
    body = r.json()
    assert body["algorithm"].startswith("ed25519")
    assert "signature" in body
    assert body["item_counts"]["domain"] >= 1
    assert isinstance(body["items"], list)


def test_erasure_foundation(client: TestClient):
    reg = client.post(
        "/v1/auth/register",
        json={"email": "erase@example.com", "password": "securepass1"},
    )
    token = reg.json()["access_token"]
    r = client.delete("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 202
    me = client.get("/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 401
