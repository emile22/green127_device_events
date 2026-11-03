#!/usr/bin/env bash
set -euo pipefail

root="${HOME}/tools/yangsuite"
venv="${root}/.venv"
if [[ ! -x "${venv}/bin/yangsuite" ]]; then
  echo "YANG Suite is not installed at ${venv}/bin/yangsuite." >&2
  exit 1
fi
if [[ ! -d "${root}/data" ]]; then
  echo "Missing YANG Suite data directory: ${root}/data" >&2
  exit 1
fi
# shellcheck disable=SC1091
source "${venv}/bin/activate"
exec "${venv}/bin/yangsuite" \
  --data-path "${root}/data" \
  --port 8480 \
  --allowed-hosts localhost