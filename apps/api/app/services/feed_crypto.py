from __future__ import annotations

import base64
import os
from functools import lru_cache
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

KEYS_DIR = Path(__file__).resolve().parent.parent / "data" / "keys"
PUBLIC_KEY_FILE = KEYS_DIR / "feed_ed25519_public.b64"
DEV_PRIVATE_KEY_FILE = KEYS_DIR / "feed_ed25519_private.dev.b64"


def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.strip())


@lru_cache(maxsize=1)
def load_public_key_bytes() -> bytes:
    if not PUBLIC_KEY_FILE.exists():
        raise FileNotFoundError(f"Missing feed public key: {PUBLIC_KEY_FILE}")
    return _b64decode(PUBLIC_KEY_FILE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_private_key_bytes() -> bytes:
    from app.config import settings

    env = os.environ.get("CGA_FEED_PRIVATE_KEY_B64") or settings.feed_private_key_b64
    if env:
        return _b64decode(env)
    if DEV_PRIVATE_KEY_FILE.exists():
        return _b64decode(DEV_PRIVATE_KEY_FILE.read_text(encoding="utf-8"))
    raise FileNotFoundError(
        "Feed private key not found. Set CGA_FEED_PRIVATE_KEY_B64 or provide "
        f"{DEV_PRIVATE_KEY_FILE} (dev only)."
    )


def sign_ed25519(payload: str) -> str:
    key = Ed25519PrivateKey.from_private_bytes(load_private_key_bytes())
    sig = key.sign(payload.encode("utf-8"))
    return base64.b64encode(sig).decode("ascii")


def verify_ed25519(payload: str, signature_b64: str, public_key_b64: str | None = None) -> bool:
    try:
        pub_bytes = _b64decode(public_key_b64) if public_key_b64 else load_public_key_bytes()
        key = Ed25519PublicKey.from_public_bytes(pub_bytes)
        key.verify(_b64decode(signature_b64), payload.encode("utf-8"))
        return True
    except (InvalidSignature, ValueError, FileNotFoundError):
        return False


def public_key_b64() -> str:
    return base64.b64encode(load_public_key_bytes()).decode("ascii")


def clear_key_cache() -> None:
    load_public_key_bytes.cache_clear()
    load_private_key_bytes.cache_clear()
