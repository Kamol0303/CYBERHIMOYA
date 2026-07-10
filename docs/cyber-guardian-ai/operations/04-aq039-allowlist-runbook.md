# AQ-039 resolution checklist (Legal + Product)

Do **not** invent IIV/UZCERT numbers or APIs.

When official allowlist arrives:

1. Set secrets (not git):
   - `CGA_EMERGENCY_SMS_ALLOWLIST=+998...` (comma-separated)
   - `CGA_EMERGENCY_API_ALLOWLIST=https://...`
   - `CGA_EMERGENCY_EMAIL_ALLOWLIST=...`
2. Keep `CGA_EMERGENCY_DRY_RUN=true` until dual-control sign-off.
3. Flip dry-run off only after Legal + Security review.
4. Mark AQ-039 `Resolved: …` in `docs/cyber-guardian-ai/assumptions-and-open-questions.md`.
5. Re-run emergency tests with a staging allowlist.

Until then: dispatch always dry-run / cabinet log only.
