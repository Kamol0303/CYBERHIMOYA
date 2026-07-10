# V1 implementation notes

## Delivered

### Sprint 1
- Monorepo: `apps/api` (FastAPI) + `apps/web` (Vite/React)
- Auth register/login JWT + `/me` + erasure foundation
- Consent GET/POST
- Guest `POST /v1/scan/url` with seed IOC + UZ scam heuristics
- `POST /v1/risk-score`
- `GET /v1/threat-feed/sync` signed stub
- Web guest scan UI + dashboard shell + uz/ru/en
- CI + defensive-only keyword gate

### Sprint 1.1 (this update)
- SQLite persistence (`CGA_DATABASE_URL`, default in-memory for tests)
- `POST /v1/scan/qr` and `POST /v1/scan/file` (client SHA-256; no binary upload required)
- Web modes: URL / QR / File hash
- Android + Windows shell stubs under `apps/android`, `apps/windows`

## Explicitly out of V1

- Full Android / Windows apps
- SMS / Telegram deep detection
- Emergency SMS to IIV (needs AQ-039)
- Production PostgreSQL / KMS
- Active probing of any kind

## Storage

SQLite now. PostgreSQL URL accepted but falls back to sqlite file until driver is wired (`sdd/03`).
