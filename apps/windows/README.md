# Cyber Guardian AI — Windows XDR shell (V1)

**Status:** scaffold only. Read-only / defensive monitoring later; no offensive tooling.

## Scope (next sprints)

- Desktop tray + scan UI (URL / file hash)
- Future: process/memory telemetry (read-only), Sigma/YARA packs
- Defensive playbooks: local block / isolate / alert only

## Suggested stack

- .NET 8 + WPF or WinUI 3
- HttpClient → `apps/api`
- Optional Windows service for feed sync

```
apps/windows/
  README.md
  docs/architecture.md
  src/CyberGuardian.Windows/Api/GuardianApiClient.cs
  src/CyberGuardian.Windows/Ui/TrayShell.cs
  src/CyberGuardian.Windows/Ui/ScanWindow.cs
```

Hard rule: defensive monitoring and local response only.
