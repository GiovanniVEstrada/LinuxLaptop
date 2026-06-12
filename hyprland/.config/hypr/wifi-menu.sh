#!/bin/bash
# IonVeil WiFi picker — wofi + nmcli

nmcli dev wifi rescan 2>/dev/null &

# Fetch network list: terse colon-separated, sorted by signal desc, deduplicated
nets=$(nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY dev wifi list 2>/dev/null \
    | sort -t: -k3 -rn \
    | awk -F: '$2!="" && !seen[$2]++')

[[ -z "$nets" ]] && { notify-send "WiFi" "No networks found" -t 3000; exit 1; }

# Build display menu: "▶ SSID 󰌾" for active+secured, "  SSID" otherwise
menu=$(echo "$nets" | awk -F: '{
    icon = ($1=="*") ? "▶ " : "  "
    lock = ($4!="" && $4!="--") ? " 󰌾" : ""
    printf "%s%s%s\n", icon, $2, lock
}')

chosen=$(echo "$menu" | wofi --dmenu \
    --prompt "  WiFi" \
    --cache-file /dev/null \
    --no-actions \
    --width 420 \
    --height 320)

[[ -z "$chosen" ]] && exit 0

# Extract SSID: strip 2-char icon prefix and optional trailing " 󰌾"
ssid=$(echo "$chosen" | cut -c3- | sed 's/ 󰌾$//' | sed 's/[[:space:]]*$//')
[[ -z "$ssid" ]] && exit 0

# Already have a saved connection — just reconnect
if nmcli -t -f NAME con show 2>/dev/null | grep -qxF "$ssid"; then
    nmcli con up id "$ssid" && notify-send "WiFi" "Connected to $ssid" -t 3000
    exit 0
fi

# New network: check if it needs a password
security=$(echo "$nets" | awk -F: -v s="$ssid" '$2==s{print $4; exit}')

if [[ -n "$security" && "$security" != "--" ]]; then
    pass=$(wofi --dmenu \
        --prompt "󰌾  $ssid" \
        --cache-file /dev/null \
        --password \
        --width 420 \
        --height 80)
    [[ -z "$pass" ]] && exit 0
    nmcli dev wifi connect "$ssid" password "$pass" \
        && notify-send "WiFi" "Connected to $ssid" -t 3000 \
        || notify-send "WiFi" "Failed to connect to $ssid" -t 4000 -u critical
else
    nmcli dev wifi connect "$ssid" \
        && notify-send "WiFi" "Connected to $ssid" -t 3000 \
        || notify-send "WiFi" "Failed to connect to $ssid" -t 4000 -u critical
fi
