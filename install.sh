#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target_dir="${HOME}"
adopt=false
dry_run=false

cd "${repo_dir}"

packages=()

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --adopt)
      adopt=true
      shift
      ;;
    --dry-run|-n)
      dry_run=true
      shift
      ;;
    --help|-h)
      cat <<'USAGE'
Usage: ./install.sh [--dry-run] [--adopt] [package...]

Links dotfiles into $HOME using GNU Stow.

Options:
  --dry-run, -n  Show what Stow would do without changing files.
  --adopt       Move existing target files into this repo, then link them.
                Review git diff after using this.
USAGE
      exit 0
      ;;
    *)
      packages+=("$1")
      shift
      ;;
  esac
done

if [[ "${#packages[@]}" -eq 0 ]]; then
  for entry in */; do
    entry="${entry%/}"
    case "${entry}" in
      packages|scripts|vscode)
        continue
        ;;
    esac

    [[ -d "${entry}" ]] && packages+=("${entry}")
  done
fi

if [[ "${#packages[@]}" -eq 0 ]]; then
  echo "No stow packages found."
  exit 1
fi

echo "Linking dotfiles into ${target_dir}:"
printf '  %s\n' "${packages[@]}"

stow_args=(--target="${target_dir}" --restow)

if [[ "${dry_run}" == true ]]; then
  stow_args+=(--simulate)
fi

if [[ "${adopt}" == true ]]; then
  stow_args+=(--adopt)
fi

stow "${stow_args[@]}" "${packages[@]}"
