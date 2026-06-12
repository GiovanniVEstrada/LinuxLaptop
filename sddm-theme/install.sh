#!/usr/bin/env bash
# Install the IonVeil SDDM theme — run with sudo
set -euo pipefail

THEME_DIR="/usr/share/sddm/themes/ionveil"
SDDM_CONF="/etc/sddm.conf.d/ionveil.conf"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $EUID -ne 0 ]]; then
  echo "Run with sudo: sudo bash $0"
  exit 1
fi

# Install SDDM if needed
if ! pacman -Q sddm &>/dev/null; then
  echo "→ Installing sddm..."
  pacman -S --noconfirm sddm
fi

# Copy theme
echo "→ Copying theme to $THEME_DIR"
rm -rf "$THEME_DIR"
cp -r "$SCRIPT_DIR/ionveil" "$THEME_DIR"

# Write SDDM config
echo "→ Writing $SDDM_CONF"
mkdir -p /etc/sddm.conf.d
cat > "$SDDM_CONF" <<'EOF'
[Theme]
Current=ionveil

[Users]
DefaultUser=gio
HideUsers=false
RememberLastUser=true
EOF

# Enable service
echo "→ Enabling sddm.service"
systemctl enable sddm.service

echo ""
echo "Done. Comment out the Hyprland auto-start in ~/.bash_profile,"
echo "then reboot to see the IonVeil login screen."
