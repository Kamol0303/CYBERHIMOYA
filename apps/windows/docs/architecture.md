# Windows shell architecture (V1 stub)

```
Tray UI
  → ScanService (URL / file hash)
    → GuardianApiClient
  → FeedSync (verify ed25519 stub → apply IOC cache)
  → (later) ReadOnlyTelemetryAgent → local IOA → alert only
```

Automated response remains local: warn user, optional network isolation hooks, never attack remote systems.
