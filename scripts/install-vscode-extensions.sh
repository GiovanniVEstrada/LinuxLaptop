#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
extensions_file="${repo_dir}/vscode/extensions.txt"

if command -v code >/dev/null 2>&1; then
  code_cmd="code"
elif command -v code-oss >/dev/null 2>&1; then
  code_cmd="code-oss"
else
  echo "VS Code CLI not found." >&2
  exit 1
fi

if [[ ! -s "${extensions_file}" ]]; then
  echo "No extensions listed at ${extensions_file}." >&2
  exit 1
fi

while IFS= read -r extension; do
  [[ -z "${extension}" ]] && continue
  "${code_cmd}" --install-extension "${extension}"
done < "${extensions_file}"

