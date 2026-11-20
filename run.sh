#!/usr/bin/env bash
# Wrapper script to execute Naukri profile updater within the virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p logs

# Activate virtualenv if present
if [ -d "$SCRIPT_DIR/.venv" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
else
    PYTHON_BIN="python3"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Naukri update job from $SCRIPT_DIR..." >> "$SCRIPT_DIR/logs/update.log"
$PYTHON_BIN update_naukri.py >> "$SCRIPT_DIR/logs/update.log" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Naukri update job finished." >> "$SCRIPT_DIR/logs/update.log"
