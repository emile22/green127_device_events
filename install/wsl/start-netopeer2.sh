#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_root="$(cd -- "$script_dir/.." && pwd)"
repo_root="$(cd -- "$install_root/.." && pwd)"
plugin_dir="$install_root/wsl/plugins"
state_file="$install_root/runtime/operational.json"
trace_file="$install_root/logs/netconf-trace.log"
connection_file="$install_root/runtime/netconf/connection.env"
mkdir -p "$install_root/runtime/netconf" "$install_root/logs"

if [[ "$EUID" -ne 0 ]]; then
  echo "Run inside Ubuntu/WSL with sudo: sudo bash install/wsl/start-netopeer2.sh" >&2
  exit 1
fi
if [[ ! -f "$plugin_dir/green_snapshot_plugin.so" ]]; then
  echo "Provider plugin is missing; run install/wsl/install-wsl.sh first." >&2
  exit 1
fi

for spec in \
  'ietf-inet-types|2013-07-15' \
  'ietf-yang-types|2013-07-15' \
  'iana-hardware|2018-03-13' \
  'ietf-power-and-energy|2026-07-02' \
  'iana-power-and-energy|2026-07-02' \
  'ietf-hardware|2018-03-13'; do
  module="${spec%%|*}"
  revision="${spec##*|}"
  installed="$(sysrepoctl -l | awk -F'|' -v module="$module" '$1 ~ "^[[:space:]]*" module "[[:space:]]*$" {gsub(/[[:space:]]/, "", $2); revision=$2} END {print revision}')"
  if [[ "$installed" != "$revision" ]]; then
    echo "Required module $module@$revision is not installed (found ${installed:-missing}); run install/yang/install-yang-modules.sh." >&2
    exit 1
  fi
done

export NP2_MODULE_DIR=/usr/share/yang/modules/netopeer2
export NP2_MODULE_PERMS=660
export NP2_MODULE_OWNER=root
export NP2_MODULE_GROUP=netconf
export SYSREPOCTL_EXECUTABLE=/usr/bin/sysrepoctl
export SYSREPOCFG_EXECUTABLE=/usr/bin/sysrepocfg
/usr/share/netopeer2/setup.sh
/usr/share/netopeer2/merge_hostkey.sh
/usr/share/netopeer2/merge_config.sh

read_config() {
  local key="$1"
  if [[ -f "$connection_file" ]]; then
    sed -n "s/^${key}=//p" "$connection_file" | head -n 1
  fi
}
username="$(read_config NETCONF_USERNAME)"
password="$(read_config NETCONF_PASSWORD)"
username="${username:-green-install-smoke}"
password="${password:-$(openssl rand -hex 24)}"
salt="$(openssl rand -hex 8)"
password_hash="$(openssl passwd -6 -salt "$salt" "$password")"
if id "$username" >/dev/null 2>&1; then
  usermod --password "$password_hash" "$username"
else
  useradd --system --no-create-home --shell /usr/sbin/nologin --password "$password_hash" "$username"
fi
netconf_host="$(hostname -I | awk '{print $1}')"
netconf_host="${netconf_host:-127.0.0.1}"
cat > "$connection_file" <<EOF
NETCONF_HOST=$netconf_host
NETCONF_PORT=830
NETCONF_USERNAME=$username
NETCONF_PASSWORD=$password
EOF
chmod 600 "$connection_file"

auth_xml="$install_root/runtime/netconf/netconf-auth.xml"
cat > "$auth_xml" <<EOF
<netconf-server xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-server">
  <listen>
    <endpoint>
      <name>default-ssh</name>
      <ssh>
        <ssh-server-parameters>
          <client-authentication>
            <supported-authentication-methods>
              <passsword/>
            </supported-authentication-methods>
            <users>
              <user>
                <name>$username</name>
                <password>$password_hash</password>
              </user>
            </users>
          </client-authentication>
        </ssh-server-parameters>
      </ssh>
    </endpoint>
  </listen>
</netconf-server>
EOF
chmod 600 "$auth_xml"
sysrepocfg --edit="$auth_xml" --datastore startup --format xml --module ietf-netconf-server
sysrepocfg --copy-from startup --module ietf-netconf-server
rm -f "$auth_xml"

systemctl set-environment \
  "SRPD_PLUGINS_PATH=$plugin_dir" \
  "GREEN_NETCONF_STATE_FILE=$state_file" \
  "GREEN_NETCONF_TRACE_FILE=$trace_file"
systemctl restart sysrepo-plugind.service
systemctl restart netopeer2.service

for attempt in $(seq 1 15); do
  if ss -ltn | awk '$4 ~ /:830$/ { found=1 } END { exit !found }'; then
    printf 'Netopeer2 is listening on TCP/830 (%s).\n' "$netconf_host"
    exit 0
  fi
  sleep 1
done
echo "Netopeer2 did not open TCP port 830." >&2
exit 1
