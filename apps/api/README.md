# Cyber Guardian AI — V1 API

Defensive-only FastAPI service.

## Endpoints

| Method | Path | Auth |
|--------|------|------|
| POST | `/v1/auth/register` | — |
| POST | `/v1/auth/token` | — |
| POST | `/v1/auth/revoke` | — |
| GET/DELETE | `/v1/me` | Bearer |
| GET/POST | `/v1/consents` | Bearer |
| POST | `/v1/scan/url` | optional |
| POST | `/v1/risk-score` | — |
| GET | `/v1/threat-feed/sync` | — |
| GET | `/health` | — |

Storage: in-memory (V1). PostgreSQL — keyingi sprint.
