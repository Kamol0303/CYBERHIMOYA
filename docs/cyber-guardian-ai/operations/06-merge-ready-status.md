# V1 merge-ready status

**Branch:** `CURSOR/v1-0-3-1-polish-b1ff` (0.4.2)  
**API version:** 0.4.2  
**PR:** https://github.com/Kamol0303/CYBERHIMOYA/pull/6  
**Verified:** 2026-07-10 (agent run)

## Automated gates

| Gate | Result |
|------|--------|
| Defensive lint | run via `make test` |
| API pytest | included in `make test` |
| Smoke `scripts/smoke_v1.py` | included in `make test` |
| Web `npm test` + `npm run build` | included in `make test` |
| Extension validate | FR-062 + FR-063 |

## 0.4.2 additions

- Behavior analyze (FR-080), MITRE filter (FR-082)
- Extension permission analyzer (FR-063)
- Windows ProcessMonitor stub (FR-070)

## Remaining human actions

1. Merge PR #6 to `main`
2. Legal: privacy/terms + AQ-039 allowlists
3. Store screenshots; production feed key rotation
