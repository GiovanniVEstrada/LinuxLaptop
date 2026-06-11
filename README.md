# Gio's Arch Linux Dotfiles

This repository contains the reproducible parts of this laptop setup:

- Window managers and desktop config: Hyprland, i3, Waybar, Polybar, Rofi, Wofi, Picom
- Terminals and shells: Kitty, Ghostty, Alacritty, Starship, tmux, zsh
- Editor config: Neovim, Code - OSS settings, and VS Code extension list
- Package manifests for Arch repo packages and AUR packages
- Backgrounds and theme files used by the config

The layout uses GNU Stow. Each top-level directory is a package whose contents mirror paths under `$HOME`.

## Use on a Fresh Arch Install

Install the base tooling first:

```sh
sudo pacman -S --needed git stow
```

Clone your repo:

```sh
git clone <your-github-repo-url> ~/dotfiles
cd ~/dotfiles
```

Install packages:

```sh
./scripts/install-packages.sh
```

Link dotfiles into `$HOME`:

```sh
./install.sh
```

Preview links first:

```sh
./install.sh --dry-run
```

On a machine that already has regular config files in place, Stow may report conflicts. To make this repo take ownership of those files:

```sh
./install.sh --adopt
git diff
```

Review the diff before committing because `--adopt` moves existing target files into the repo.

Install VS Code extensions:

```sh
./scripts/install-vscode-extensions.sh
```

## Daily Workflow

After changing config on this laptop, refresh the generated package and extension lists:

```sh
./scripts/export-state.sh
git status
```

Then review and commit the changes.

## GitHub Remote

This checkout currently has an existing `origin` remote. To point it at your own GitHub repository:

```sh
git remote set-url origin git@github.com:<your-user>/<your-repo>.git
git push -u origin master
```

Use the HTTPS URL instead if you prefer HTTPS remotes.

## Notes

Do not commit private keys, tokens, browser profiles, password stores, `.env` files, or app session directories. This repo should contain reproducible configuration, not personal credentials or cache state.
