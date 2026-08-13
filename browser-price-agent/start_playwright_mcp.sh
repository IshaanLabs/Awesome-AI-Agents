#!/usr/bin/env bash
# Starts Playwright MCP for the price_agent smoke test (WSL/Linux).
# Keep this terminal open while running smoke_test.py

set -euo pipefail

echo "[mcp] Loading nvm (need Node 18+; system node is too old) ..."
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ -s "$NVM_DIR/nvm.sh" ]; then
  # shellcheck disable=SC1090
  . "$NVM_DIR/nvm.sh"
  nvm use 20 >/dev/null || nvm use 24 >/dev/null || nvm use default
else
  echo "[mcp] WARNING: nvm not found; using whatever node is on PATH"
fi

echo "[mcp] node=$(node -v) npm=$(npm -v) npx=$(command -v npx)"
echo "[mcp] Ensuring MCP browser (chrome-for-testing) is installed ..."
npx --yes @playwright/mcp@latest install-browser chrome-for-testing

# Default MCP --browser is "chrome" -> /opt/google/chrome/chrome (missing in WSL).
# Point at the chrome-for-testing binary Playwright MCP just installed.
CHROME_BIN="$(ls -d "$HOME"/.cache/ms-playwright/chromium-*/chrome-linux64/chrome 2>/dev/null | sort -V | tail -n 1 || true)"
if [ -z "${CHROME_BIN}" ] || [ ! -x "${CHROME_BIN}" ]; then
  echo "[mcp] ERROR: chrome-for-testing binary not found under ~/.cache/ms-playwright"
  exit 1
fi

echo "[mcp] Using executable: ${CHROME_BIN}"
echo "[mcp] Starting @playwright/mcp on port 8931 (headless) ..."
echo "[mcp] Keep this terminal open while running smoke_test.py"
echo "[mcp] If port 8931 is busy, kill the old server first: pkill -f 'playwright-mcp'"

exec npx --yes @playwright/mcp@latest \
  --executable-path "${CHROME_BIN}" \
  --headless \
  --isolated \
  --port 8931
