#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -s "${repo_dir}/packages/pacman.txt" ]]; then
  mapfile -t pacman_packages < "${repo_dir}/packages/pacman.txt"
  sudo pacman -S --needed "${pacman_packages[@]}"
fi

if [[ -s "${repo_dir}/packages/aur.txt" ]]; then
  if ! command -v yay >/dev/null 2>&1; then
    echo "AUR packages are listed in packages/aur.txt, but yay is not installed." >&2
    echo "Install yay first, then rerun this script." >&2
    exit 1
  fi

  mapfile -t aur_packages < "${repo_dir}/packages/aur.txt"
  yay -S --needed "${aur_packages[@]}"
fi
