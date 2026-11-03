#!/usr/bin/env bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Run inside Ubuntu/WSL with sudo: sudo bash install/wsl/stop-netopeer2.sh" >&2
  exit 1
fi
systemctl stop netopeer2.service sysrepo-plugind.service
systemctl unset-environment SRPD_PLUGINS_PATH GREEN_NETCONF_STATE_FILE GREEN_NETCONF_TRACE_FILE
printf 'Stopped Sysrepo/Netopeer2 services; install runtime state and credentials were retained.\n'
