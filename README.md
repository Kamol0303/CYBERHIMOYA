# CYBERHIMOYA / Cyber Guardian AI

Mudofaa-only xavfsizlik ekotizimi (Android + Windows + Web). **Hujum / exploit / C2 vositalari yo‘q.**

## Holat

| Qatlam | Holat |
|--------|-------|
| Spec (APEX v5.3) | `docs/cyber-guardian-ai/` |
| V1 API | `apps/api` — Auth, scan URL/QR/file, feed CDN, SQLite/Postgres |
| V1 Web | `apps/web` — URL/QR/file skan, login, tarix, rozilik, feed, uz/ru/en |
| Client shells | `apps/android`, `apps/windows` — Gradle/csproj + API/UI stubs |
| Ops | `docs/.../04-aq039-allowlist-runbook.md` |

## Tezkor ishga tushirish

### API

```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ixtiyoriy
uvicorn app.main:app --reload --port 8000
```

- Health: `GET http://127.0.0.1:8000/health`
- Docs: `http://127.0.0.1:8000/docs`
- SQLite fayl: `CGA_DATABASE_URL=sqlite:///./data/cga.db` (default)

### Web

```bash
cd apps/web
npm install
npm run dev
```

Brauzer: `http://127.0.0.1:5173` (Vite `/v1` ni API ga proxy qiladi).

### Docker

```bash
docker compose up --build
# optional Postgres:
docker compose --profile postgres up -d db
# CGA_DATABASE_URL=postgresql://cga:cga@db:5432/cga docker compose up --build api web
```

API `:8000`, Web `:8080`. Feed CDN: `http://127.0.0.1:8000/cdn/feeds/`.

### Testlar

```bash
cd apps/api && PYTHONPATH=. pytest -q
cd apps/web && npm test && npm run build
bash scripts/defensive-lint.sh
```

## Birinchi sprint (V1)

1. Auth + Consent (+ erasure foundation)  
2. `POST /v1/scan/url|qr|file` + risk score + MITRE / scam family  
3. Threat feed sync (signed delta stub)  
4. Web mehmon skan + login + dashboard tarix/rozilik + i18n  
5. Guest rate-limit + CI + defensive-only lint  
6. Android/Windows shell stubs + ed25519 feed + on-device SMS foundation  

Keyingi: AQ-039 rasmiy allowlist (Legal), Compose/WinUI production, SMS runtime binding.

## Hujjatlar

1. [`docs/cyber-guardian-ai/APEX-MASTER-SPEC.md`](docs/cyber-guardian-ai/APEX-MASTER-SPEC.md)  
2. [`docs/cyber-guardian-ai/acceptance-checklist.md`](docs/cyber-guardian-ai/acceptance-checklist.md)  
3. [`docs/cyber-guardian-ai/README.md`](docs/cyber-guardian-ai/README.md)  
4. [`docs/cyber-guardian-ai/operations/04-aq039-allowlist-runbook.md`](docs/cyber-guardian-ai/operations/04-aq039-allowlist-runbook.md)  
