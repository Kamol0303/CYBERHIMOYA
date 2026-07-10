# V1 implementation notes

## Delivered

### Sprint 1–1.2
- API: auth, consent, URL/QR/file scan, risk-score, scans history, guest rate-limit
- SQLite persistence + Web login/dashboard/i18n
- Docker Compose (api + web)
- Android/Windows shell docs

### Sprint 1.10 (this update)
- Play Data safety + MS Partner Center drafts
- Screenshot capture guides
- Merge-ready status doc (`06-merge-ready-status.md`)
- Release checklist marked verified for automated gates

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

- Live IIV/UZCERT SMS/API without AQ-039 Legal values
- Cloud SMS upload
- Full Play/Microsoft Store submission (listings drafted only)
- Production private feed key in git
- Active probing of any kind
