# Changelog

## 0.3.0 — 2026-07-10

P0 user tools + passive hunting metadata (FR-043 / FR-051 / FR-003 / FR-MX01).

- `POST /v1/messages/suspicious` — PII-minimized message report + heuristics
- `POST /v1/breach-check` — offline seed breach lookup (email hash only)
- `POST/GET/DELETE /v1/devices` — linked device registry (+ web revoke)
- Scan responses: `intent_tags`, `campaign_id`, `kill_chain_stage` (incl. QR non-URL)
- Web: message preview confirm, breach i18n, guest `sessionStorage` history
- File scan `run_yara` stub (name heuristic, no yara-python)

## 0.2.1 — 2026-07-10

Follow-up after PR #1–#3 on `main`: RFC 7807 errors, offline banner, account erasure UI.

- Auth 401 + guest 429 as RFC 7807 `ProblemDetail`
- Web: ProblemDetail.detail on errors, offline banner, account erasure UI
- Extension popup shows API `detail` on 429
- PWA PNG icons + apple-touch-icon; smoke 401/429 + version pin
- OpenAPI `HTTPBearer` scheme + `MetricsResponse` schema
- Minimal PWA service worker (shell cache; `/v1/*` network-only)
- Extension 429 i18n + packaging validate script
- CI: extension validate + Docker compose smoke (incl. SW/icons)
- Remove unused feed `20260710.1`
- Android/Windows README accuracy; nginx `X-CGA-Defensive-Only` parity

## 0.2.0 — 2026-07-10

- V1 defensive platform: API, Web, extension, Android/Windows shells
- ed25519 threat-feed CDN
- Emergency consent/confirm/dispatch (dry-run until AQ-039)
- CORS `chrome-extension://*` via `allow_origin_regex` (API + Docker)
- Web guest 429 + reason/action i18n; emergency status i18n
- Extension icons + stable unpacked `key`
- PWA manifest, store listing/data-safety stubs, smoke/`make test`
- Security headers, `/v1/metrics`, Docker healthchecks
- Merge-ready status documentation (PR #1 → `main`)

## 0.1.0 — 2026-07-10

- Initial API + Web MVP scaffold
