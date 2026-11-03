#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -eq 0 ]]; then
  echo "Run as the regular WSL user; sudo is used only for apt prerequisites." >&2
  exit 1
fi

if [[ ! -r /etc/os-release ]]; then
  echo "Cannot identify the Linux distribution." >&2
  exit 1
fi
. /etc/os-release
if [[ "${ID:-}" != ubuntu || "${VERSION_ID:-}" != 22.04 ]]; then
  echo "Expected Ubuntu 22.04; found ${PRETTY_NAME:-unknown}." >&2
  exit 1
fi

root="${HOME}/tools/yangsuite"
venv="${root}/.venv"
mkdir -p "${root}/data" "${root}/logs" "${root}/config" "${root}/cache/pip"

sudo apt-get install -y python3-pip python3-venv python3-lxml

if [[ ! -x "${venv}/bin/python" ]]; then
  python3 -m venv "${venv}"
fi
export PIP_CACHE_DIR="${root}/cache/pip"
# shellcheck disable=SC1091
source "${venv}/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install \
  'yangsuite==3.0.14' \
  'yangsuite-netconf==1.17.27' \
  'yangsuite-devices==2.9.16' \
  'yangsuite-filemanager==1.9.13' \
  'yangsuite-yangtree==2.1.12'
python -m pip check
yangsuite --configure-only --save-settings \
  --data-path "${root}/data" \
  --port 8480 \
  --allowed-hosts localhost
yangsuite --help >/dev/null
printf 'YANG Suite environment configured under %s\n' "${root}"