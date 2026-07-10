# V1 implementation notes

## Delivered

### Sprint 1–1.2
- API: auth, consent, URL/QR/file scan, risk-score, scans history, guest rate-limit
- SQLite persistence + Web login/dashboard/i18n
- Docker Compose (api + web)
- Android/Windows shell docs

### Sprint 1.8 (this update)
- `scripts/smoke_v1.py` + `Makefile`
- Chrome MV3 extension guest scan (`apps/extension`)
- V1 release/merge checklist

## Emergency dry-run

Until Legal resolves AQ-039, `CGA_EMERGENCY_*_ALLOWLIST=PENDING_AQ039` and
`CGA_EMERGENCY_DRY_RUN=true` keep all dispatches as cabinet logs only.

## Postgres local

```bash
docker compose --profile postgres up -d db
export CGA_DATABASE_URL=postgresql://cga:cga@127.0.0.1:5432/cga
cd apps/api && uvicorn app.main:app --reload
```

## Feed keys

```bash
python scripts/generate_feed_keys.py
python scripts/generate_feed.py
```

## Explicitly out of V1

- Full native apps UI (Compose/WinUI production screens)
- Cloud SMS upload / live IIV SMS without AQ-039
- Production private key in git
- Active probing of any kind
