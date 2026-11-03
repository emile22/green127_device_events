#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="${HOME}/tools/yangsuite"
venv="${root}/.venv"
lock="$(cd -- "${script_dir}/.." && pwd)/requirements.lock.txt"
report="$(cd -- "${script_dir}/.." && pwd)/version-report.txt"
if [[ ! -x "${venv}/bin/python" ]]; then
  echo "Missing YANG Suite Python environment: ${venv}" >&2
  exit 1
fi
# shellcheck disable=SC1091
source "${venv}/bin/activate"
python -m pip check
temporary_lock="$(mktemp "${lock}.XXXXXX")"
temporary_report="$(mktemp "${report}.XXXXXX")"
trap 'rm -f "${temporary_lock}" "${temporary_report}"' EXIT
python -m pip freeze --all | sort > "${temporary_lock}"
{
  printf 'Capture date: %s\n' "$(date --iso-8601=seconds)"
  . /etc/os-release
  printf 'Operating system: %s\n' "${PRETTY_NAME:-unknown}"
  printf 'Python: %s\n' "$(python --version 2>&1)"
  printf 'pip: %s\n' "$(python -m pip --version)"
  for package in yangsuite yangsuite-netconf yangsuite-devices yangsuite-filemanager yangsuite-yangtree Django ncclient paramiko; do
    python -m pip show "${package}" | awk -F ': ' '$1 == "Name" || $1 == "Version" { print }'
  done
} > "${temporary_report}"
mv "${temporary_lock}" "${lock}"
mv "${temporary_report}" "${report}"
trap - EXIT
printf 'Wrote %s and %s\n' "${lock}" "${report}"