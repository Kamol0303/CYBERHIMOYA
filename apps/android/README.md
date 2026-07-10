# Cyber Guardian AI — Android shell (V1)

**Status:** scaffold only. Defensive client; no offensive tooling.

## Scope (next sprints)

- Minimal permissions; local-first
- Guest / signed-in URL + QR scan via API
- On-device SMS heuristics later (never upload raw SMS)
- Consent gates for monitoring / emergency reporting

## Suggested stack

- Kotlin + Jetpack Compose
- Retrofit/Ktor → `apps/api` `/v1/*`
- Signed threat-feed delta sync

## Local API

Point `CGA_API_BASE` to `http://10.0.2.2:8000` on emulator.

Stub client: `src/main/java/uz/cyberguardian/android/api/GuardianApi.kt`

```
apps/android/
  README.md
  docs/architecture.md
  src/main/java/.../GuardianApi.kt
```

Do not add offensive tooling.
