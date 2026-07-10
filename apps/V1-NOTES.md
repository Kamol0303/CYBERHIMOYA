# V1 implementation notes

## Delivered (sprint 1)

- Monorepo: `apps/api` (FastAPI) + `apps/web` (Vite/React)
- Auth register/login JWT + `/me` + erasure foundation
- Consent GET/POST
- Guest `POST /v1/scan/url` with seed IOC + UZ scam heuristics (payment/gov/emergency)
- `POST /v1/risk-score`
- `GET /v1/threat-feed/sync` signed stub
- Web guest scan UI + dashboard shell + uz/ru/en
- CI + defensive-only keyword gate

## Explicitly out of V1

- Android / Windows clients
- SMS / Telegram deep detection
- Emergency SMS to IIV (needs AQ-039)
- PostgreSQL / production KMS
- Active probing of any kind

## Storage

In-memory process store — replace with PostgreSQL per `sdd/03`.
