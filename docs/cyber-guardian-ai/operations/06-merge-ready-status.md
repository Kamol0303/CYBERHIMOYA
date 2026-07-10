# V1 merge-ready status

**Branch:** `main` (PR #1 merged) + follow-up `CURSOR/v1-post-merge-polish-b1ff`  
**API version:** 0.2.1  
**Verified:** 2026-07-10 (agent run)

## Automated gates

| Gate | Result |
|------|--------|
| Defensive lint | PASS |
| API pytest | 27 passed |
| Smoke `scripts/smoke_v1.py` | 15/15 |
| Web `npm test` + `npm run build` | PASS |
| Extension validate | PASS |

## Checklist mapping (`05-v1-release-checklist.md`)

- [x] `make test` equivalent run
- [x] `/health` → `defensive_only: true`
- [x] Feed ed25519 + verify path covered in smoke
- [x] Emergency dry-run enforced (AQ-039 pending)
- [x] Defensive keyword gate
- [x] README run instructions present
- [x] AQ-039 not invented — template/runbook only
- [x] PR #1 merged to `main`

## Remaining human actions

1. Legal: finalize privacy/terms; resolve AQ-039 allowlist values
2. Capture real store screenshots; submit Play/MS when ready
3. Rotate feed keys for production (`CGA_FEED_PRIVATE_KEY_B64`)

## Do not merge blockers

None technical for V1 dry-run scope. Legal AQ-039 is **not** a code merge blocker while dry-run remains default.
