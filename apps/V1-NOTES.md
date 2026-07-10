# V1 implementation notes

## Delivered

### Sprint 1–1.2
- API: auth, consent, URL/QR/file scan, risk-score, scans history, guest rate-limit
- SQLite persistence + Web login/dashboard/i18n
- Docker Compose (api + web)
- Android/Windows shell docs

### Sprint 1.4 (this update)
- Real **ed25519** feed signing/verify (`feed_crypto.py`)
- Dev keypair under `app/data/keys/` + `CGA_FEED_PRIVATE_KEY_B64` override
- Feed version `20260710.2`, `/v1/threat-feed/public-key`
- Android Compose UI shell + **on-device SMS** analyzer (raw SMS never uploaded)
- Windows tray UI shell stub

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
- Cloud SMS upload
- Emergency SMS to IIV (AQ-039)
- Production private key in git
- Active probing of any kind
