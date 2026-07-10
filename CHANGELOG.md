# Changelog

## 0.4.4 — 2026-07-10

- `GET /v1/scans?verdict=&scan_type=` — FR-092 history filters
- `POST /v1/retention/prune` — NFR-040 risk history retention (180d default)
- Android `WifiAnalyzer` stub (FR-061)
- Windows `UsbMonitor` + `RansomwareMonitor` stubs (FR-073/074)
- Web: scan verdict filter + prune CTA

## 0.4.3 — 2026-07-10

- `GET /v1/sigma/rules` — FR-081 catalog stub (metadata only)
- `POST /v1/notifications/read-all`
- Web: sigma list + mark-all-read

## 0.4.2 — 2026-07-10

- `POST /v1/behavior/analyze` — FR-080 correlate recent scans/threats
- `GET /v1/threat-events?mitre=` — FR-082 MITRE filter
- Extension FR-063 permission analyzer (`management` + `analyzer.js`)
- Windows `ProcessMonitor` stub (FR-070 detect/warn only)
- Web: behavior CTA + MITRE filter on activity

## 0.4.1 — 2026-07-10

- `POST/GET/DELETE /v1/dns/*` — FR-060 domain check + user allowlist (audit)
- Web dashboard DNS allowlist UI
- Extension: local IOC cache from threat-feed sync (+ offline seed) for faster FR-062 warnings
- Password health: local pwned seed (`pwned_local`, never logged)
- Metrics: threat_event / notification / domain_allowlist counts
- `GET /v1/me/stats` — dashboard counters; extension popup IOC sync status

## 0.4.0 — 2026-07-10

Activity layer: threat events, notifications, JSON reports (FR-090/091/092/093).

- `GET /v1/threat-events` — emit on authenticated suspicious/malicious scans
- `GET /v1/notifications` + `POST /{id}/read` — in-app alerts (body keys, no raw PII)
- `POST/GET /v1/reports` — redacted JSON export
- `GET /v1/scans/{id}` — scan detail
- `POST /v1/password-health` — FR-050 strength check (never stored/logged)
- `GET /v1/risk-score/history` — authenticated risk trail (scan-derived + POST /risk-score)
- Extension FR-062: background nav scan + phishing page banner + session allowlist
- Web dashboard: activity, notifications, report export, password health, risk history
- Includes 0.3.1 polish: guest history, device revoke, QR hunting, YARA stub

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
