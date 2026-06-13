#!/bin/bash
chosen=$(printf "  Shutdown\n  Reboot\n  Logout" | wofi --dmenu \
    --prompt "Power" \
    --cache-file /dev/null \
    --no-actions \
    --width 220 \
    --height 152)

case "$chosen" in
    *Shutdown) systemctl poweroff ;;
    *Reboot)   systemctl reboot ;;
    *Logout)   hyprctl dispatch exit ;;
esac
