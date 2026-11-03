#!/usr/bin/env bash
set -euo pipefail

root="${HOME}/tools/yangsuite"
venv="${root}/.venv"
if [[ ! -x "${venv}/bin/python" ]]; then
  echo "Missing YANG Suite Python environment: ${venv}" >&2
  exit 1
fi
# shellcheck disable=SC1091
source "${venv}/bin/activate"
python --version
python -m pip --version
python -m pip show yangsuite yangsuite-netconf yangsuite-devices yangsuite-filemanager yangsuite-yangtree Django ncclient paramiko
python -m pip check
yangsuite --help >/dev/null

status="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' http://localhost:8480/ || true)"
case "${status}" in
  2??|3??) printf 'YANG Suite HTTP status: %s\n' "${status}" ;;
  *) echo "YANG Suite is not reachable at http://localhost:8480 (HTTP ${status:-no response})." >&2; exit 1 ;;
esac