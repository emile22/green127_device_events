#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_root="$(cd -- "$script_dir/.." && pwd)"
repo_root="$(cd -- "$install_root/.." && pwd)"
yang_source="$repo_root/allrun5/yang"
manifest="$script_dir/yang-modules-manifest.txt"

if [[ "$EUID" -ne 0 ]]; then
  echo "Run inside Ubuntu/WSL with sudo: sudo bash install/yang/install-yang-modules.sh" >&2
  exit 1
fi
command -v sysrepoctl >/dev/null || { echo "sysrepoctl is missing; run install/wsl/install-wsl.sh first." >&2; exit 1; }

module_revision() {
  local module="$1"
  sysrepoctl -l | awk -F'|' -v module="$module" '$1 ~ "^[[:space:]]*" module "[[:space:]]*$" {gsub(/[[:space:]]/, "", $2); revision=$2} END {print revision}'
}

while IFS='|' read -r module revision filename hash _; do
  [[ -z "$module" || "$module" == \#* ]] && continue
  module="$(echo "$module" | xargs)"
  revision="$(echo "$revision" | xargs)"
  filename="$(echo "$filename" | xargs | sed 's#^allrun5/yang/##')"
  source_file="$yang_source/$filename"
  if [[ ! -f "$source_file" ]]; then
    echo "Pinned YANG source is missing: $source_file" >&2
    exit 1
  fi
  actual_hash="$(sha256sum "$source_file" | awk '{print $1}')"
  if [[ "$actual_hash" != "$(echo "$hash" | xargs)" ]]; then
    echo "SHA256 mismatch for $module ($filename); refusing to install modified input." >&2
    exit 1
  fi

  installed_revision="$(module_revision "$module")"
  if [[ -n "$installed_revision" && "$installed_revision" != "$revision" ]]; then
    echo "Sysrepo already has $module@$installed_revision; pinned revision is $revision. Refusing silent replacement." >&2
    exit 1
  fi
  if [[ "$installed_revision" == "$revision" ]]; then
    printf 'Already installed: %s@%s\n' "$module" "$revision"
  else
    printf 'Installing: %s@%s\n' "$module" "$revision"
    sysrepoctl -a -i "$source_file" -s "$yang_source"
  fi
done < "$manifest"

# Parent links are RFC 8348 configuration data; keep this explicit hierarchy
# separate from Energy Object relationships and runtime operational snapshots.
sysrepocfg --edit="$script_dir/hardware-hierarchy.xml" --datastore startup --format xml --module ietf-hardware
sysrepocfg --copy-from startup --module ietf-hardware

printf '\nInstalled pinned modules:\n'
sysrepoctl -l | grep -E '^(iana-hardware|iana-power-and-energy|ietf-hardware|ietf-inet-types|ietf-power-and-energy|ietf-yang-types)[[:space:]]'
