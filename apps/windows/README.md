# Cyber Guardian AI — Windows XDR shell (V1)

**Status:** scaffold only. Read-only / defensive monitoring later; no offensive tooling.  
**Version:** aligned with monorepo V1 (`0.2.x`).

## Scope (next sprints)

- Desktop tray + scan UI (URL / file hash)
- Process monitoring stub: `Monitoring/ProcessMonitor.cs` (FR-070, detect/warn only)
- Future: Sigma/YARA packs, registry/USB hooks
- Defensive playbooks: local block / isolate / alert only

## Suggested stack

- .NET 8 + WPF (`net8.0-windows`)
- HttpClient → `apps/api` via `Api/GuardianApiClient.cs`
- Optional Windows service for feed sync

**Build note:** WPF requires a **Windows** host (`dotnet build` / `dotnet run`). Linux CI does not build this project.

```
apps/windows/
  README.md
  docs/architecture.md
  docs/dotnet.md
  src/CyberGuardian.Windows/Api/GuardianApiClient.cs
  src/CyberGuardian.Windows/Ui/TrayShell.cs
  src/CyberGuardian.Windows/Ui/ScanWindow.cs
```

Hard rule: defensive monitoring and local response only.
