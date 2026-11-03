#!/usr/bin/env bash
set -euo pipefail

force_install=0
if [[ "${1:-}" == "--force-package-install" ]]; then
  force_install=1
elif [[ $# -gt 0 ]]; then
  echo "Usage: sudo bash install/wsl/install-wsl.sh [--force-package-install]" >&2
  exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_root="$(cd -- "$script_dir/.." && pwd)"
repo_root="$(cd -- "$install_root/.." && pwd)"
source "$script_dir/source-versions.env"

if [[ "${ID:-}" != "ubuntu" && -r /etc/os-release ]]; then
  . /etc/os-release
fi
if [[ "${ID:-}" != "ubuntu" || "${VERSION_ID:-}" != "$WSL_RELEASE" ]]; then
  echo "Expected Ubuntu $WSL_RELEASE, found ${PRETTY_NAME:-unknown}." >&2
  exit 1
fi
if [[ "$EUID" -ne 0 ]]; then
  echo "Run from WSL with sudo: sudo bash install/wsl/install-wsl.sh" >&2
  exit 1
fi

specs=()
needs_apt=0
while IFS= read -r spec || [[ -n "$spec" ]]; do
  [[ -z "$spec" || "$spec" == \#* ]] && continue
  package="${spec%%=*}"
  expected="${spec#*=}"
  installed="$(dpkg-query -W -f='${Version}' "$package" 2>/dev/null || true)"
  candidate="$(apt-cache policy "$package" | awk '/Candidate:/ {candidate=$2} END {print candidate}')"
  if [[ "$candidate" != "$expected" ]]; then
    echo "APT candidate mismatch for $package: expected $expected, found ${candidate:-none}." >&2
    exit 1
  fi
  if [[ "$installed" == "$expected" ]]; then
    printf 'OK %s=%s\n' "$package" "$installed"
    continue
  fi
  if [[ -n "$installed" && "$force_install" -ne 1 ]]; then
    echo "$package is $installed but lock requires $expected; rerun with --force-package-install to change it." >&2
    exit 1
  fi
  needs_apt=1
  specs+=("$spec")
done < "$install_root/wsl/apt-packages-lock.txt"

if [[ "$needs_apt" -eq 1 ]]; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${specs[@]}"
fi

pkg-config --exists sysrepo libyang
plugin_dir="$install_root/wsl/plugins"
mkdir -p "$plugin_dir"
cc $(pkg-config --cflags sysrepo libyang) \
  -std=c11 -Wall -Wextra -Werror -fPIC -shared \
  "$repo_root/allrun5/netconf/green_snapshot_plugin.c" \
  -o "$plugin_dir/green_snapshot_plugin.so" \
  $(pkg-config --libs sysrepo libyang)

printf 'WSL packages match the recorded lock.\n'
printf 'Installed prefix: %s\n' "$INSTALL_PREFIX"
printf 'Built provider: %s\n' "$plugin_dir/green_snapshot_plugin.so"
