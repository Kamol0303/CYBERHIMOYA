# V1 implementation notes

## Delivered

### Sprint 1–1.2
- API: auth, consent, URL/QR/file scan, risk-score, scans history, guest rate-limit
- SQLite persistence + Web login/dashboard/i18n
- Docker Compose (api + web)
- Android/Windows shell docs

### Sprint 1.3 (this update)
- PostgreSQL store (`psycopg`) via `CGA_DATABASE_URL=postgresql://...`
- `create_store()` factory (sqlite | postgres)
- Local threat-feed CDN: `/cdn/feeds/{version}.json` + `/v1/threat-feed/delta|verify`
- Signed feed pack generation (`scripts/generate_feed.py`)
- Compose profile `postgres` for optional Postgres 16
- Native API client stubs (Kotlin + C#)

## Postgres local

```bash
docker compose --profile postgres up -d db
export CGA_DATABASE_URL=postgresql://cga:cga@127.0.0.1:5432/cga
cd apps/api && uvicorn app.main:app --reload
```

## Explicitly out of V1

- Full native apps UI
- SMS / Telegram deep detection
- Emergency SMS to IIV (AQ-039)
- Production ed25519 keys / KMS
- Active probing of any kind
