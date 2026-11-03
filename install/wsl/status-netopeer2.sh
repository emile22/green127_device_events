#!/usr/bin/env bash
set -euo pipefail
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
install_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
source "$install_root/wsl/source-versions.env"
. /etc/os-release
printf 'WSL distribution: %s %s\n' "$PRETTY_NAME" "$VERSION_ID"
printf 'libyang: %s\n' "$(pkg-config --modversion libyang 2>/dev/null || echo unavailable)"
printf 'libnetconf2 package: %s\n' "$(dpkg-query -W -f='${Version}' libnetconf2-2 2>/dev/null || echo unavailable)"
printf 'Sysrepo: %s\n' "$(pkg-config --modversion sysrepo 2>/dev/null || echo unavailable)"
printf 'Netopeer2: %s\n' "$(dpkg-query -W -f='${Version}' netopeer2 2>/dev/null || echo unavailable)"
for service in sysrepo-plugind.service netopeer2.service; do
  if systemctl is-active --quiet "$service"; then printf '%s: running\n' "$service"; else printf '%s: stopped\n' "$service"; fi
done
printf '\nSysrepo modules:\n'
sysrepoctl -l
printf '\nNETCONF listener:\n'
ss -ltn | awk '$4 ~ /:830$/ {print $4}'
printf 'WSL address fallback: %s\n' "$(hostname -I | awk '{print $1}')"
