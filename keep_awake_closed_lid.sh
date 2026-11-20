#!/usr/bin/env bash
# Configures Ubuntu/GNOME so closing the laptop lid does NOT suspend the system.
# The screen will turn off, but background tasks, Wi-Fi, cron, and Docker will keep running!

echo "Configuring laptop to stay awake when lid is closed..."

# 1. Update GNOME desktop settings (does not require sudo)
if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.settings-daemon.plugins.power lid-close-ac-action 'nothing'
    echo "✓ GNOME lid-close action on AC (plugged in) set to: 'nothing' (stay awake)"
    
    # Optional: also on battery
    gsettings set org.gnome.settings-daemon.plugins.power lid-close-battery-action 'nothing'
    echo "✓ GNOME lid-close action on Battery set to: 'nothing' (stay awake)"
fi

# 2. Configure systemd-logind drop-in (requires sudo)
LOGIND_CONF_DIR="/etc/systemd/logind.conf.d"
LOGIND_FILE="$LOGIND_CONF_DIR/naukri-lid.conf"

echo ""
echo "To ensure system-level background execution when the lid is closed,"
echo "we will add a systemd-logind rule ($LOGIND_FILE)."
echo "You may be prompted for your sudo password:"

sudo mkdir -p "$LOGIND_CONF_DIR"
sudo tee "$LOGIND_FILE" > /dev/null <<EOF
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
EOF

sudo systemctl restart systemd-logind

echo ""
echo "=========================================================="
echo "✓ DONE! Your laptop will now stay awake with lid closed."
echo "Your automated jobs (8 AM and 5 PM) will run uninterrupted."
echo "=========================================================="
