# Android shell architecture (V1 stub)

```
UI (Compose)
  → ScanRepository (URL / QR / file hash)
    → GuardianApi (/v1/scan/*)
  → ConsentStore (DataStore)
  → FeedSyncWorker
       → GET /v1/threat-feed/sync
       → download delta_url (/cdn/feeds/{ver}.json)
       → verify signature → apply local IOC cache
```

All network calls are defensive reputation / sync. No outbound probing of third-party hosts beyond the Cyber Guardian API and signed CDN feed URLs.

See `src/main/java/uz/cyberguardian/android/api/GuardianApi.kt`.
