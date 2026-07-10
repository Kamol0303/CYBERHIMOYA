# V1 release / merge checklist

## V1 automated gates (PR #1 merged to `main`)

- [x] `make test` (lint + API pytest + web build + smoke) — verified 2026-07-10
- [x] `GET /health` → `defensive_only: true`
- [x] Feed: `algorithm=ed25519`, verify path in smoke
- [x] Emergency: allowlist pending ⇒ dispatch `dry_run: true` only
- [x] No offensive keywords in `apps/**` source (`scripts/defensive-lint.sh`)
- [x] README run instructions still accurate
- [x] AQ-039 still open unless Legal provided real allowlist (do not invent)

See also: [`06-merge-ready-status.md`](06-merge-ready-status.md)

## Manual spot checks

1. Web guest URL scan (malicious seed domain)
2. Register → consent → emergency confirm/dispatch dry-run
3. Extension popup scan against local API (optional)
4. Docker: `docker compose up --build` (optional)

## Explicit non-goals until later

- Live IIV/UZCERT SMS/API (AQ-039)
- Cloud SMS upload
- Full Play Store / Microsoft Store packaging submission
