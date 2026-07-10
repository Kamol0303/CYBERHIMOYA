#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "== Defensive-only keyword gate =="
if command -v rg >/dev/null 2>&1; then
  if rg -n -i --glob '!**/tests/**' --glob '!**/docs/**' \
    'exploit.?poc|hack.?back|ddos.?tool|metasploit|reverse.?shell|c2.?implant' \
    apps 2>/dev/null; then
    echo "FAIL: offensive keywords in apps/"
    exit 1
  fi
fi
echo "OK"
