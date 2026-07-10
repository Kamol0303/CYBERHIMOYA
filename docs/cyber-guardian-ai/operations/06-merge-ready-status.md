# V1 merge-ready status

**Branch:** `CURSOR/v1-stage-next-b1ff` (0.3.0)  
**API version:** 0.3.0  
**Verified:** 2026-07-10 (agent run)

## Automated gates

| Gate | Result |
|------|--------|
| Defensive lint | PASS |
| API pytest | 35 passed |
| Smoke `scripts/smoke_v1.py` | 24/24 |
| Web `npm test` + `npm run build` | PASS |
| Extension validate | PASS |

## 0.3.0 additions

- Suspicious message report, breach-check, devices
- Hunting metadata on scans (`intent_tags`, `campaign_id`)

## Remaining human actions

1. Merge this PR to `main`
2. Legal: privacy/terms + AQ-039 allowlists
3. Store screenshots; production feed key rotation
