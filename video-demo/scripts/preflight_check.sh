#!/usr/bin/env bash
# Diagnostic only: reports which capture/mux tools are present and how to install
# whatever's missing. Never installs anything itself — installing a global tool is
# a decision the agent should surface, not take silently.
set -u

ok=0
missing=0

check() {
  local name="$1" hint="$2"
  if command -v "$name" >/dev/null 2>&1; then
    echo "[ok]      $name"
    ok=$((ok + 1))
  else
    echo "[missing] $name — $hint"
    missing=$((missing + 1))
  fi
}

echo "=== always required ==="
check ffmpeg   "install via your OS package manager (apt/brew install ffmpeg)"
check ffprobe  "ships with ffmpeg — reinstall ffmpeg if only this is missing"
check python3  "install via your OS package manager"

echo
echo "=== needed for CLI/terminal capture ==="
check vhs "go install github.com/charmbracelet/[email protected] (or: brew install vhs)"

echo
echo "=== needed for web app capture ==="
if command -v npx >/dev/null 2>&1; then
  echo "[ok]      npx"
  ok=$((ok + 1))
  if npx --yes playwright --version >/dev/null 2>&1; then
    echo "[ok]      playwright"
    ok=$((ok + 1))
  else
    echo "[missing] playwright — npx --yes playwright install chromium"
    missing=$((missing + 1))
  fi
else
  echo "[missing] npx — install Node.js"
  missing=$((missing + 1))
fi

echo
echo "$ok ok, $missing missing"
[ "$missing" -eq 0 ]
