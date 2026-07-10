# CYBERHIMOYA / Cyber Guardian AI

Mudofaa-only xavfsizlik ekotizimi (Android + Windows + Web). **Hujum / exploit / C2 vositalari yo‘q.**

## Holat

| Qatlam | Holat |
|--------|-------|
| Spec (APEX v5.3) | `docs/cyber-guardian-ai/` |
| V1 API | `apps/api` — Auth, Consent, `POST /v1/scan/url`, risk-score, threat-feed sync |
| V1 Web | `apps/web` — mehmon URL skan, dashboard qobiq, uz/ru/en |

## Tezkor ishga tushirish

### API

```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Health: `GET http://127.0.0.1:8000/health`
- Docs: `http://127.0.0.1:8000/docs`

### Web

```bash
cd apps/web
npm install
npm run dev
```

Brauzer: `http://127.0.0.1:5173` (Vite `/v1` ni API ga proxy qiladi).

### Testlar

```bash
cd apps/api && pytest -q
cd apps/web && npm test && npm run build
bash scripts/defensive-lint.sh
```

## Birinchi sprint (V1)

1. Auth + Consent (+ erasure foundation)  
2. `POST /v1/scan/url` + risk score + MITRE / scam family skeleton  
3. Threat feed sync (signed delta stub)  
4. Web mehmon skan + dashboard shell + i18n  
5. CI + defensive-only lint  

Keyingi: Android/Windows shell, QR/file scan, PostgreSQL.

## Hujjatlar

1. [`docs/cyber-guardian-ai/APEX-MASTER-SPEC.md`](docs/cyber-guardian-ai/APEX-MASTER-SPEC.md)  
2. [`docs/cyber-guardian-ai/acceptance-checklist.md`](docs/cyber-guardian-ai/acceptance-checklist.md)  
3. [`docs/cyber-guardian-ai/README.md`](docs/cyber-guardian-ai/README.md)  
