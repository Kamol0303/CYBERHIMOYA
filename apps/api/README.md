# Cyber Guardian AI — V1 API

Defensive-only FastAPI service (no intrusion tooling).

## Storage

- **Default:** SQLite (`CGA_DATABASE_URL=sqlite:///./data/cga.db`)
- **Optional:** Postgres (`postgresql://…`) via `psycopg` / `docker compose --profile postgres`
- Tests use `sqlite:///:memory:` (`tests/conftest.py`)

## CORS

`CGA_CORS_ORIGINS` is a comma list. Exact origins go to `allow_origins`.
Token `chrome-extension://*` expands to `allow_origin_regex` so the MV3 popup can call the API.

## Endpoints

| Method | Path | Auth |
|--------|------|------|
| GET | `/health` | — |
| POST | `/v1/auth/register` | — |
| POST | `/v1/auth/token` | — |
| POST | `/v1/auth/revoke` | Bearer |
| GET/DELETE | `/v1/me` | Bearer |
| GET | `/v1/me/stats` | Bearer |
| POST | `/v1/behavior/analyze` | Bearer |
| GET | `/v1/sigma/rules` | — |
| POST | `/v1/notifications/read-all` | Bearer |
| GET/POST | `/v1/consents` | Bearer |
| POST | `/v1/scan/url` | optional |
| POST | `/v1/scan/qr` | optional |
| POST | `/v1/scan/file` | optional |
| GET | `/v1/scans` | Bearer |
| POST | `/v1/risk-score` | — |
| GET | `/v1/threat-feed/sync` | — |
| GET | `/v1/threat-feed/delta/{version}` | — |
| GET | `/v1/threat-feed/verify` | — |
| GET | `/v1/threat-feed/public-key` | — |
| GET | `/cdn/feeds/{version}.json` | — |
| GET | `/v1/emergency/allowlist` | — |
| POST | `/v1/emergency/consent` | Bearer |
| POST | `/v1/emergency/confirm` | Bearer |
| POST | `/v1/emergency/dispatch` | Bearer |
| GET | `/v1/emergency/logs` | Bearer |
| GET | `/v1/metrics` | — |
| POST | `/v1/messages/suspicious` | optional |
| POST | `/v1/breach-check` | optional |
| POST | `/v1/devices/register` | Bearer |
| GET | `/v1/devices` | Bearer |
| DELETE | `/v1/devices/{id}` | Bearer |
| GET | `/v1/threat-events` | Bearer |
| GET | `/v1/threat-events/{id}` | Bearer |
| GET | `/v1/notifications` | Bearer |
| POST | `/v1/notifications/{id}/read` | Bearer |
| POST | `/v1/reports` | Bearer |
| GET | `/v1/reports/{id}` | Bearer |
| GET | `/v1/scans/{id}` | Bearer |
| POST | `/v1/password-health` | — (never stored) |
| GET | `/v1/risk-score/history` | Bearer |
| POST | `/v1/dns/check` | Bearer |
| GET/POST/DELETE | `/v1/dns/allowlist` | Bearer |

Scan responses may include hunting fields: `intent_tags`, `campaign_id`, `kill_chain_stage`.
`POST /v1/scan/file` accepts `run_yara` (V1 stub heuristics, no yara-python).
Authenticated scans also append `risk_score_history` rows (FR-020 trail).

Emergency dispatch stays **dry-run** until AQ-039 allowlists are set (env only).

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
