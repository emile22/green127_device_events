#!/usr/bin/env bash
set -euo pipefail

for service in sysrepo-plugind.service netopeer2.service; do
  if systemctl is-active --quiet "$service"; then
    printf '%s: running\n' "$service"
  else
    printf '%s: stopped\n' "$service"
  fi
done
sysrepoctl -l | grep -E '^(ietf-power-and-energy|iana-power-and-energy|ietf-hardware|iana-hardware)[[:space:]]' || true
ss -ltn | awk '$4 ~ /:830$/ { print "NETCONF listener: " $4 }'