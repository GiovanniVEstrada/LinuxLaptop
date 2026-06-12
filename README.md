# gio's dotfiles — IonVeil

> tech-noir Arch Linux setup built around Hyprland.

Dark, minimal, intentional. Every piece themed to the same palette — deep space backgrounds, cyan accents, pink highlights, glass blur.

---

## Stack

| Layer | Tool |
|---|---|
| WM | Hyprland |
| Bar | Waybar |
| Launcher | Wofi |
| Terminal | Kitty |
| Shell | Zsh + Starship |
| Lock screen | Hyprlock |
| Idle manager | Hypridle |
| Wallpaper | awww |
| System monitor | Btop |
| System info | Fastfetch |
| Display manager | SDDM |

## IonVeil Palette

```
bg       #05070b    surface  #090e18
text     #f6f8ff    muted    #aab4c8
cyan     #6ee7ff    blue     #7c9cff
pink     #ff6bd6    green    #95f3c3
red      #ff6b6b    yellow   #ffd700
```

## Keybinds

| Key | Action |
|---|---|
| `Super + Enter` | Terminal (Kitty) |
| `Super + D` | App launcher (Wofi) |
| `Super + W` | WiFi picker |
| `Super + L` | Lock screen |
| `Print` | Screenshot → `~/Pictures/Screenshots/` |
| `Shift + Print` | Region screenshot → file |
| `Ctrl + Print` | Region screenshot → clipboard |

---

## Install on a Fresh Arch Setup

```sh
sudo pacman -S --needed git stow
git clone https://github.com/GiovanniVEstrada/dotfiles ~/dotfiles
cd ~/dotfiles
```

Link everything with Stow:

```sh
stow hyprland hyprlock hyprpaper kitty waybar wofi starship fastfetch btop backgrounds
```

If there are existing config conflicts:

```sh
stow --adopt hyprland   # moves existing files into the repo first
git diff                # review before committing
```

---

## Structure

Each top-level directory is a Stow package — its contents mirror paths under `$HOME`.

```
dotfiles/
├── backgrounds/    wallpapers
├── btop/           system monitor theme + config
├── fastfetch/      system info, orbital logo, greeter animation
├── hyprland/       WM config, keybinds, window rules, wifi-menu script
├── hyprlock/       lock screen + hypridle config
├── hyprmocha/      IonVeil variable definitions
├── hyprpaper/      wallpaper config
├── kitty/          terminal config + IonVeil theme + shell wrapper
├── sddm-theme/     display manager theme
├── starship/       shell prompt
├── waybar/         status bar config + IonVeil styles
└── wofi/           launcher styles
```

---

> Do not commit private keys, tokens, `.env` files, or session state. This repo is configuration only.
