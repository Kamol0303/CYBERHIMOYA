# Microsoft Store Partner Center — Product properties (draft)

| Property | Value |
|----------|-------|
| Product type | App |
| Category | Security |
| Subcategory | PC security |
| Markets | Uzbekistan first (expand TBD) |
| Pricing | Free (Plus TBD — AQ-003) |
| Age rating | Suitable for young children / 3+ |
| Privacy policy URL | TBD — use `docs/privacy-policy-draft.md` until Legal finalizes |
| Support contact | TBD |

## Capabilities declaration

- `internetClient` — API scan/feed
- No webcam/mic by default
- No broadFileSystemAccess in V1 shell

## Package

```bash
cd apps/windows/src/CyberGuardian.Windows
dotnet publish -c Release -r win-x64 --self-contained false
```

MSIX packaging: TBD after publisher identity is registered.
