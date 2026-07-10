# Feed signing keys

| File | Purpose |
|------|---------|
| `feed_ed25519_public.b64` | Public key — embed in Android/Windows/Web clients |
| `feed_ed25519_private.dev.b64` | **DEV ONLY** private key for local + CI |

Production:
1. `python scripts/generate_feed_keys.py --force` on a secure host
2. Set `CGA_FEED_PRIVATE_KEY_B64` in secrets
3. Distribute new public key to clients
4. Never commit production private keys

Algorithm: **ed25519** (NFR-011).
