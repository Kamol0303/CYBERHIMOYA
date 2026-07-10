# Android shell architecture (V1 stub)

```
UI (Compose)
  → ScanRepository (URL / QR / file hash)
    → ApiClient (/v1/scan/*)
  → ConsentStore (DataStore)
  → FeedSyncWorker (signed delta only)
```

All network calls are defensive reputation / sync. No outbound probing of third-party hosts beyond the Cyber Guardian API and signed CDN feed URLs.
