# Troubleshooting

## WSL or Distribution Missing

Check `wsl --status` and `wsl -l -v`. The kit does not enable Windows features automatically. From an elevated PowerShell, install WSL and the required distribution separately, then reboot if requested:

```powershell
wsl --install
wsl --install -d Ubuntu-22.04
```

## Python Version or Imports Fail

Check `py -0p`; the kit requires Python 3.11. Run `install/windows/install-windows.ps1` again. Use the explicit interpreter `install/windows/.venv/Scripts/python.exe` rather than a policy-blocked global `python` command.

## APT Version Drift

`install/wsl/install-wsl.sh` compares each installed and candidate package against `wsl/apt-packages-lock.txt`. It fails rather than silently switching versions. Only use `--force-package-install` when an explicit package change is intended and reviewed.

## YANG Revision Conflict

`install/yang/install-yang-modules.sh` refuses to replace a different installed revision. Inspect `sysrepoctl -l`; do not delete modules blindly. The current modules and hashes are listed in `yang/yang-modules-manifest.txt`.

## Netopeer2 Is Not Listening

Run `sudo bash install/wsl/status-netopeer2.sh`, then inspect the unit logs:

```bash
sudo journalctl -u sysrepo-plugind.service -n 100 --no-pager
sudo journalctl -u netopeer2.service -n 100 --no-pager
```

Start with `sudo bash install/wsl/start-netopeer2.sh`. The script requires the native install and exact YANG modules first.

## Windows Cannot Reach NETCONF

The client first tries `localhost:830`; if that fails, it tries the current `NETCONF_HOST` recorded in `install/runtime/netconf/connection.env`. The WSL address can change after WSL restarts, so rerun `start-netopeer2.sh` and do not hard-code an old address. Check Windows firewall policy if both attempts fail.

## Credentials

The smoke password is stored only in `install/runtime/netconf/connection.env` with restrictive WSL permissions. Never print or commit it. Regenerate by removing this file and restarting Netopeer2; the installer will create a new local smoke user/password and update Sysrepo configuration.
