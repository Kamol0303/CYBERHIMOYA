#!/usr/bin/env bash
# Validate MV3 extension packaging (icons + manifest paths).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXT="$ROOT/apps/extension"
MANIFEST="$EXT/manifest.json"

test -f "$MANIFEST"
python3 - <<'PY' "$EXT"
import json, sys
from pathlib import Path
ext = Path(sys.argv[1])
manifest = json.loads((ext / "manifest.json").read_text(encoding="utf-8"))
paths = set()
for size, rel in (manifest.get("icons") or {}).items():
    paths.add(rel)
action_icons = (manifest.get("action") or {}).get("default_icon") or {}
for size, rel in action_icons.items():
    paths.add(rel)
missing = [p for p in sorted(paths) if not (ext / p).is_file()]
if missing:
    raise SystemExit(f"missing icon files: {missing}")
if not (ext / "popup.html").is_file() or not (ext / "popup.js").is_file():
    raise SystemExit("popup.html / popup.js required")
if "key" not in manifest:
    raise SystemExit("manifest key missing (stable unpacked ID)")
print("OK extension packaging", len(paths), "icons")
PY
