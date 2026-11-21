#!/usr/bin/env bash
# Sets up a systemd user timer with Persistent=true
# Unlike cron, if your laptop is asleep or off at 8:00 AM or 5:00 PM,
# it will automatically trigger the update the moment you open/turn on your laptop!

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

mkdir -p "$SYSTEMD_USER_DIR"

# 1. Create service file
cat <<EOF > "$SYSTEMD_USER_DIR/naukri-updater.service"
[Unit]
Description=Naukri Profile & Resume Auto-Updater
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$SCRIPT_DIR
ExecStart=/bin/bash $SCRIPT_DIR/run.sh
EOF

# 2. Create timer file (runs at 09:00 and 17:00, with Persistent=true to catch up if asleep)
cat <<EOF > "$SYSTEMD_USER_DIR/naukri-updater.timer"
[Unit]
Description=Timer for Naukri Profile & Resume Auto-Updater

[Timer]
OnCalendar=*-*-* 09:00:00
OnCalendar=*-*-* 17:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Reload and enable systemd user daemon
systemctl --user daemon-reload
systemctl --user enable --now naukri-updater.timer

echo "=========================================================="
echo "Systemd user timer installed successfully!"
echo "Status of your timer:"
systemctl --user list-timers --all | grep naukri
echo "=========================================================="
echo "Benefit: If your laptop is asleep/closed at 8 AM or 5 PM,"
echo "it will catch up and run automatically as soon as it wakes!"
echo "=========================================================="
