# V1 release / merge checklist

## Before merge to `main`

- [ ] `make test` (lint + API pytest + web build + smoke)
- [ ] `GET /health` → `defensive_only: true`
- [ ] Feed: `algorithm=ed25519`, `/v1/threat-feed/verify` → `valid: true`
- [ ] Emergency: allowlist pending ⇒ dispatch `dry_run: true` only
- [ ] No offensive keywords in `apps/**` source (`scripts/defensive-lint.sh`)
- [ ] README run instructions still accurate
- [ ] AQ-039 still open unless Legal provided real allowlist (do not invent)

## Manual spot checks

1. Web guest URL scan (malicious seed domain)
2. Register → consent → emergency confirm/dispatch dry-run
3. Extension popup scan against local API (optional)
4. Docker: `docker compose up --build` (optional)

## Explicit non-goals until later

- Live IIV/UZCERT SMS/API (AQ-039)
- Cloud SMS upload
- Full Play Store / Microsoft Store packaging
