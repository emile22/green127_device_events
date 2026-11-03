# Environment Architecture

The working setup deliberately separates Windows Python from WSL native services.

```text
Windows 11
  install/windows/.venv
    allrun5 GREEN source via temporary PYTHONPATH
    pytest / pyang / ncclient
          |
          | NETCONF over SSH, localhost:830 first
          | dynamically detected WSL address fallback
          v
Ubuntu 22.04 under WSL 2
  Netopeer2 server
       |
  Sysrepo + sysrepo-plugind
       |
  libyang / libnetconf2
       |
  allrun5 read-only operational-data provider
```

The Python runtime writes an RFC 7951 combined snapshot. A native C Sysrepo plugin parses the snapshot against the installed YANG schemas and returns the hardware or GREEN operational subtree. Netopeer2 serves NETCONF over SSH. `ncclient` runs only on Windows.

Native packages were installed from Ubuntu apt under `/usr`; Sysrepo repository is `/etc/sysrepo`. The plugin is built from the read-only source `allrun5/netconf/green_snapshot_plugin.c` into `install/wsl/plugins/` by the kit. Runtime snapshots and generated credentials use `install/runtime/`; traces use `install/logs/`.

No container runtime or Docker configuration is used. Control operations remain outside NETCONF; verification issues `<get>` only.
