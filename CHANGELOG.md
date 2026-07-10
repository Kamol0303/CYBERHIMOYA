# Changelog

## 0.2.1 — 2026-07-10

- Guest 429 returns RFC 7807 `ProblemDetail` (`application/problem+json`)
- PWA PNG icons + apple-touch-icon; smoke 429 + version pin
- OpenAPI `HTTPBearer` scheme + `MetricsResponse` schema
- Minimal PWA service worker (shell cache; `/v1/*` network-only)
- Extension 429 i18n + packaging validate script
- CI: extension validate + Docker compose smoke job
- Smoke: feed verify/CDN + frame security header
- Android/Windows README accuracy; Android `versionName` 0.2.0-v1-shell
- nginx `X-CGA-Defensive-Only` parity

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
