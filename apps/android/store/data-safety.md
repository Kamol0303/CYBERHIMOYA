# Google Play Data safety form (draft answers)

| Question | Answer | Notes |
|----------|--------|-------|
| Does the app collect/share user data? | Yes (limited) | Account email if registered; scan hashes |
| Is data encrypted in transit? | Yes | TLS to API |
| Can users request deletion? | Yes | `DELETE /v1/me` erasure foundation |
| SMS / call logs collected? | **No cloud collection** | On-device heuristics only |
| Location? | No | |
| Photos/videos? | Optional local file hash only | Bytes not uploaded in V1 hash path |
| Personal info sold? | No | |
| Security practices | Data encrypted in transit; defensive-only product | |

## Data types

| Type | Collected | Shared | Purpose |
|------|-----------|--------|---------|
| Email | Optional (account) | No | Auth |
| App activity (scan hashes) | Yes | No (internal TI) | Fraud/security |
| Device IDs | Not in V1 shell | — | — |

## Permissions declarations

See `play-listing.md`. `SEND_SMS` declared but runtime-gated on emergency consent + AQ-039.
