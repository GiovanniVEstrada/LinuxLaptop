#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "${repo_dir}/packages" "${repo_dir}/vscode"

pacman -Qqen | sort > "${repo_dir}/packages/pacman.txt"
pacman -Qqem | sort > "${repo_dir}/packages/aur.txt"

if command -v code >/dev/null 2>&1; then
  code --list-extensions | sort > "${repo_dir}/vscode/extensions.txt"
elif command -v code-oss >/dev/null 2>&1; then
  code-oss --list-extensions | sort > "${repo_dir}/vscode/extensions.txt"
else
  echo "VS Code CLI not found; skipped vscode/extensions.txt" >&2
fi

echo "Exported package and VS Code extension state."

