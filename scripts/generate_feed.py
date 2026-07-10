#!/usr/bin/env python3
"""Regenerate signed threat-feed pack under apps/api/app/data/feeds/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "api"
sys.path.insert(0, str(ROOT))

from app.services.feed import ensure_feed_files  # noqa: E402
from app.services.feed_crypto import clear_key_cache  # noqa: E402


def main() -> None:
    clear_key_cache()
    path = ensure_feed_files()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
