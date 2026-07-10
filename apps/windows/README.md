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
```

Hard rule: no exploit development, no hack-back, no active intrusion.
