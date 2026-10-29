#!/usr/bin/env bash
set -euo pipefail

systemctl stop netopeer2.service sysrepo-plugind.service
systemctl unset-environment SRPD_PLUGINS_PATH GREEN_NETCONF_STATE_FILE
echo "Stopped the minrun4 NETCONF services."