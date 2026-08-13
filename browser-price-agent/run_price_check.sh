#!/usr/bin/env bash
# Run price check with the WSL venv at /mnt/d/AI_Expo/ram_ram

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="${VENV:-/mnt/d/AI_Expo/ram_ram}"

echo "[run] Activating venv: $VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "[run] python=$(command -v python) ($(python -V))"
echo "[run] Starting check_price.py ..."
exec python "$ROOT/price_check/check_price.py"
