# Cyber Guardian AI — Android shell (V1)

**Status:** scaffold only. Defensive client; no offensive tooling.  
**Version:** `0.2.0-v1-shell` (aligned with monorepo V1).

## Scope (next sprints)

- Minimal permissions; local-first
- Guest / signed-in URL + QR scan via API
- On-device SMS heuristics (`sms/OnDeviceSmsAnalyzer.kt` — raw SMS never uploaded)
- Wi-Fi analyzer stub (`wifi/WifiAnalyzer.kt`, FR-061 — warn only, no probing)
- Consent gates for monitoring / emergency reporting

## Suggested stack

- Kotlin + Jetpack Compose
- Retrofit/Ktor → `apps/api` `/v1/*`
- Signed threat-feed delta sync

## Local API

Point `CGA_API_BASE` to `http://10.0.2.2:8000` on emulator.

| Layer | Path |
|-------|------|
| Interface | `api/GuardianApi.kt` |
| HTTP impl | `api/HttpGuardianApi.kt` (wired from `MainActivity`) |
| UI shell | `ui/Screens.kt` (Compose stubs — uncomment deps in Studio) |
| SMS on-device | `sms/OnDeviceSmsAnalyzer.kt` (raw SMS never uploaded) |

See `docs/android-studio.md` to enable Compose.

Do not add offensive tooling.
