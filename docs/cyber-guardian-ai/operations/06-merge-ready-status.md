# V1 merge-ready status

**Branch:** `CURSOR/v1-0-3-1-polish-b1ff` (0.4.0)  
**API version:** 0.4.0  
**Verified:** 2026-07-10 (agent run)

## Automated gates

| Gate | Result |
|------|--------|
| Defensive lint | run via `make test` |
| API pytest | included in `make test` |
| Smoke `scripts/smoke_v1.py` | included in `make test` |
| Web `npm test` + `npm run build` | included in `make test` |
| Extension validate | FR-062 content script + background |

## 0.4.0 additions

- Threat events, notifications, reports
- Password health (FR-050), scan detail, risk-score history
- Extension phishing banner (FR-062)

## Remaining human actions

1. Merge this PR to `main`
2. Legal: privacy/terms + AQ-039 allowlists
3. Store screenshots; production feed key rotation
