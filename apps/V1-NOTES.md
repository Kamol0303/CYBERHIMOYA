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

### Sprint 1.1
- SQLite persistence (`CGA_DATABASE_URL`)
- `POST /v1/scan/qr` and `POST /v1/scan/file` (client SHA-256)
- Web modes: URL / QR / File hash
- Android + Windows shell stubs

### Sprint 1.2 (this update)
- `GET /v1/scans` authenticated history
- Guest scan rate limit (429)
- Web login/register + consent toggles + scan history
- Default SQLite file DB for runtime; in-memory for tests
- `docker-compose.yml` + Dockerfiles

## Explicitly out of V1

- Full Android / Windows apps
- SMS / Telegram deep detection
- Emergency SMS to IIV (needs AQ-039)
- Production PostgreSQL / KMS
- Active probing of any kind
