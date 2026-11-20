#!/usr/bin/env bash
# Helper script to display base64 encoded strings for GitHub Secrets

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================================"
echo "GitHub Secrets Generator for Naukri Auto-Updater"
echo "================================================================"

if [ -f "session.json" ]; then
    echo "1. Secret Name: NAUKRI_SESSION_B64"
    echo "Copy the value below and paste into GitHub Repo Settings -> Secrets -> Actions:"
    echo "----------------------------------------------------------------"
    base64 -w 0 session.json
    echo ""
    echo "----------------------------------------------------------------"
else
    echo "[!] session.json not found. Run python auth_login.py first."
fi

echo ""

RESUME_FILE=$(find resumes/ -type f \( -name "*.pdf" -o -name "*.docx" \) | head -n 1)
if [ -n "$RESUME_FILE" ] && [ -f "$RESUME_FILE" ]; then
    echo "2. Secret Name: RESUME_B64 (from $RESUME_FILE)"
    echo "Copy the value below and paste into GitHub Repo Settings -> Secrets -> Actions:"
    echo "----------------------------------------------------------------"
    base64 -w 0 "$RESUME_FILE"
    echo ""
    echo "----------------------------------------------------------------"
else
    echo "[!] No resume found in resumes/ directory."
fi
