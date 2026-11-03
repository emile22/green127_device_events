#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_root="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/source-versions.env"
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
. /etc/os-release
failures=0

check() {
  local label="$1" actual="$2" expected="$3"
  if [[ "$actual" == "$expected" ]]; then
    printf '[PASS] %s: %s\n' "$label" "$actual"
  else
    printf '[FAIL] %s: expected %s, found %s\n' "$label" "$expected" "${actual:-unavailable}"
    failures=$((failures + 1))
  fi
}

check "Ubuntu release" "${VERSION_ID:-}" "$WSL_RELEASE"
for package_spec in build-essential pkg-config libssh-dev libyang2 libyang2-dev \
  libyang2-tools libnetconf2-2 libsysrepo-dev sysrepo sysrepo-plugind netopeer2; do
  expected="$(awk -F= -v p="$package_spec" '$1 == p {print $2; exit}' "$install_root/wsl/apt-packages-lock.txt")"
  actual="$(dpkg-query -W -f='${Version}' "$package_spec" 2>/dev/null || true)"
  check "apt $package_spec" "$actual" "$expected"
done
check "libyang pkg-config" "$(pkg-config --modversion libyang 2>/dev/null || true)" "$LIBYANG_VERSION"
check "Sysrepo pkg-config" "$(pkg-config --modversion sysrepo 2>/dev/null || true)" "$SYSREPO_VERSION"
check "Netopeer2 server version" "$(dpkg-query -W -f='${Version}' netopeer2 2>/dev/null | sed 's/-.*//')" "$NETOPEER2_VERSION"
check "libnetconf2 package version" "$(dpkg-query -W -f='${Version}' libnetconf2-2 2>/dev/null | sed 's/-.*//')" "$LIBNETCONF2_VERSION"

for tool in yanglint sysrepoctl sysrepocfg netopeer2-server netopeer2-cli; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '[PASS] command available: %s (%s)\n' "$tool" "$(command -v "$tool")"
  else
    printf '[FAIL] command unavailable: %s\n' "$tool"
    failures=$((failures + 1))
  fi
done

module_revision() {
  local module="$1"
  sysrepoctl -l | awk -F'|' -v module="$module" '$1 ~ "^[[:space:]]*" module "[[:space:]]*$" {gsub(/[[:space:]]/, "", $2); revision=$2} END {print revision}'
}
while IFS='|' read -r module revision _; do
  [[ -z "$module" || "$module" == \#* ]] && continue
  module="$(echo "$module" | xargs)"
  revision="$(echo "$revision" | xargs)"
  actual="$(module_revision "$module")"
  check "Sysrepo module $module" "$actual" "$revision"
done < "$install_root/yang/yang-modules-manifest.txt"

for service in sysrepo-plugind.service netopeer2.service; do
  if systemctl is-active --quiet "$service"; then
    printf '[PASS] systemd service active: %s\n' "$service"
  else
    printf '[FAIL] systemd service inactive: %s\n' "$service"
    failures=$((failures + 1))
  fi
done
if ss -ltn | awk '$4 ~ /:830$/ { found=1 } END { exit !found }'; then
  printf '[PASS] NETCONF SSH listener: TCP/830\n'
else
  printf '[FAIL] NETCONF SSH listener missing: TCP/830\n'
  failures=$((failures + 1))
fi
printf 'WSL address fallback: %s\n' "$(hostname -I | awk '{print $1}')"

if [[ "$failures" -gt 0 ]]; then
  printf 'WSL verification failed: %s check(s).\n' "$failures" >&2
  exit 1
fi
printf 'WSL verification passed.\n'
