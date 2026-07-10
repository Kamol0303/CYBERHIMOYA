# Windows shell architecture (V1 stub)

```
Tray UI
  → ScanService (URL / file hash)
    → GuardianApiClient
  → FeedSync
       → /v1/threat-feed/sync
       → download delta_url
       → FeedVerifier → local IOC cache
  → (later) ReadOnlyTelemetryAgent → local IOA → alert only
```

See `src/CyberGuardian.Windows/Api/GuardianApiClient.cs`.

Automated response remains local: warn user, optional network isolation hooks, never attack remote systems.
