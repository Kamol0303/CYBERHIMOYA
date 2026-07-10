# Cyber Guardian AI — Browser extension (MV3)

Defensive guest URL scan for the active tab, plus a phishing-page banner (FR-062).
No page rewriting beyond the banner root, no credential capture.

## Load (Chrome/Edge)

1. Start API: `cd apps/api && uvicorn app.main:app --port 8000`
2. `chrome://extensions` → Developer mode → Load unpacked → `apps/extension`
3. Open a page → extension popup → **Joriy sahifani tekshirish**
4. Navigating to a known-malicious seed domain shows a top banner (dismiss / session allow)

Set `API_BASE` in `popup.js` and `background.js` if API is remote.

**CORS:** API / Docker `CGA_CORS_ORIGINS` includes `chrome-extension://*` (expanded to
`allow_origin_regex`). For production, pin the published extension ID instead of the wildcard.

**Stable unpacked ID:** `manifest.json` includes a public `key` (private PEM is `key.pem`).
Regenerate with:

```bash
openssl genrsa -out key.pem 2048
openssl rsa -in key.pem -pubout -outform DER | openssl base64 -A
```

Paste the base64 into `manifest.json` `"key"`.

**V1 scope:** content-script warning banner + session allowlist + local IOC cache
(from `/v1/threat-feed/sync`, with offline seed fallback). No enterprise policy push,
no network blocking via declarativeNetRequest.
