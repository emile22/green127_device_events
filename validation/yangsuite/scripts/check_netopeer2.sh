#!/usr/bin/env bash
set -euo pipefail

port="${NETCONF_PORT:-830}"
if ! command -v ss >/dev/null 2>&1; then
  echo "The ss command is unavailable; install the Ubuntu iproute2 package." >&2
  exit 1
fi
if ! ss -ltnH "sport = :${port}" | grep -q .; then
  echo "No TCP listener found on port ${port}. Netopeer2 was not changed." >&2
  exit 1
fi
ss -ltnp "sport = :${port}"