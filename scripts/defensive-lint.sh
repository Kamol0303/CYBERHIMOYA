#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "== Defensive-only keyword gate (source only) =="
# Docs may mention forbidden capabilities as prohibitions; scan code only.
if grep -RIn -E 'exploit.?poc|hack.?back|ddos.?tool|metasploit|reverse.?shell|c2.?implant' \
  --include='*.py' --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' \
  --include='*.kt' --include='*.cs' --include='*.java' \
  --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=dist --exclude-dir=__pycache__ \
  apps 2>/dev/null; then
  echo "FAIL: offensive keywords in apps/ source"
  exit 1
fi
echo "OK"
