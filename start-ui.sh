#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Detect OS
OS="$(uname -s)"

# Check for Python 3
if ! command -v python3 &>/dev/null; then
  echo "Python 3 is not installed or not in PATH."
  if [ "$OS" = "Darwin" ]; then
    echo "Install it via Homebrew: brew install python"
  else
    echo "Install it via your package manager, e.g.: sudo apt install python3 python3-venv"
  fi
  exit 1
fi

# Create venv if missing
if [ ! -f ".venv/bin/python" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

# Auto-detect browser and set HTML2PDF_BROWSER
if [ "$OS" = "Darwin" ]; then
  CHROME_PATHS=(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
  )
else
  CHROME_PATHS=(
    "/usr/bin/google-chrome"
    "/usr/bin/google-chrome-stable"
    "/usr/bin/chromium-browser"
    "/usr/bin/chromium"
    "/snap/bin/chromium"
  )
fi

for p in "${CHROME_PATHS[@]}"; do
  if [ -f "$p" ] || [ -x "$p" ]; then
    export HTML2PDF_BROWSER="$p"
    break
  fi
done

echo "Starting app at http://127.0.0.1:5000"

# Open browser in background after a short delay
if [ "$OS" = "Darwin" ]; then
  (sleep 1 && open "http://127.0.0.1:5000") &
else
  (sleep 1 && xdg-open "http://127.0.0.1:5000") &
fi

.venv/bin/python app.py
