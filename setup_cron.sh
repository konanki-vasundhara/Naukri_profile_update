#!/usr/bin/env bash
# Sets up crontab for daily execution at 8:00 AM and 5:00 PM (17:00)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_SCRIPT="$SCRIPT_DIR/run.sh"

chmod +x "$RUN_SCRIPT"

# Cron jobs:
# 0 9 * * * -> 9:00 AM daily
# 0 17 * * * -> 5:00 PM daily
CRON_JOB_1="0 9 * * * /bin/bash $RUN_SCRIPT"
CRON_JOB_2="0 17 * * * /bin/bash $RUN_SCRIPT"

echo "Configuring cron jobs for Naukri update..."

# Create a temporary file with existing crontab without previous NaukriAI entries
CURRENT_CRON=$(crontab -l 2>/dev/null | grep -v "$RUN_SCRIPT" || true)

# Write updated crontab
(
    echo "$CURRENT_CRON"
    echo "# Naukri Daily Profile & Resume Auto-Updater (9:00 AM and 5:00 PM)"
    echo "$CRON_JOB_1"
    echo "$CRON_JOB_2"
) | sed '/^$/N;/^\n$/D' | crontab -

echo "Crontab updated successfully! Current scheduled jobs:"
crontab -l | grep "$RUN_SCRIPT"
echo ""
echo "Done! The update script will now automatically run daily at 9:00 AM and 5:00 PM."
