#!/usr/bin/env bash
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────────
VENV_DIR="venv"
APP_FILE="app.py"

# Move to the directory this script lives in
cd "$(dirname "$0")"

# ── Step 1: Create venv if it doesn't exist ───────────────────────────────────
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "      Virtual environment created."
else
    echo "[1/3] Virtual environment already exists, skipping creation."
fi

# ── Step 2: Activate venv ─────────────────────────────────────────────────────
echo "[2/3] Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# ── Step 3: Install / update dependencies ─────────────────────────────────────
echo "[3/3] Installing dependencies from requirements.txt..."
pip install -r requirements.txt --timeout 120 --quiet

# ── Launch ────────────────────────────────────────────────────────────────────
echo ""
echo "Starting Cyclistic Dashboard..."
echo "Open your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the server."
echo ""
streamlit run "$APP_FILE"
