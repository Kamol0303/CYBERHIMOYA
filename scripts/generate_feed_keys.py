#!/usr/bin/env python3
"""Generate or regenerate ed25519 feed signing keys (dev helper)."""

from __future__ import annotations

import argparse
import base64
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

ROOT = Path(__file__).resolve().parents[1] / "apps" / "api" / "app" / "data" / "keys"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ed25519 feed keypair")
    parser.add_argument("--force", action="store_true", help="Overwrite existing keys")
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    pub_path = ROOT / "feed_ed25519_public.b64"
    priv_path = ROOT / "feed_ed25519_private.dev.b64"
    if pub_path.exists() and priv_path.exists() and not args.force:
        print(f"Keys already exist in {ROOT} (use --force to rotate)")
        return
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    priv_raw = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    priv_path.write_text(base64.b64encode(priv_raw).decode("ascii") + "\n", encoding="utf-8")
    pub_path.write_text(base64.b64encode(pub_raw).decode("ascii") + "\n", encoding="utf-8")
    print(f"Wrote {pub_path}")
    print(f"Wrote {priv_path} (DEV ONLY)")
    print("Rotate production via CGA_FEED_PRIVATE_KEY_B64; never commit prod private keys.")


if __name__ == "__main__":
    main()
