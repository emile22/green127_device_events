# Cisco YANG Suite validation checkpoint

## Status

This is a partial installation and validation record, not an acceptance pass. WSL previously mounted the Ubuntu disk read-only and the venv contained zero-byte files. On 2026-11-02, the pinned YANG Suite packages and dependencies were reinstalled; the root filesystem reported `rw`, the CLI help succeeded, and `pip check` reported no broken requirements.

The Windows launcher then started the service, and `http://localhost:8480` returned HTTP 200 (`text/html; charset=utf-8`). The listener was verified on `127.0.0.1:8480`, not all interfaces. This verifies the web endpoint only. NETCONF connection, server hello, schema retrieval, and GREEN data validation remain incomplete.

## First-run email prompt

The installed YANG Suite onboarding handler rejects addresses containing `@gmail` and responds with HTTP 500 and a company-email validation message. Use a legitimate company-managed address; this response is the installed handler's validation behavior, not a server startup or database failure. Do not record the address in repository files.

## Architecture

```text
Windows 11 browser
        |
        | http://localhost:8480
        v
WSL Ubuntu-22.04
  Cisco YANG Suite
        |
        | NETCONF/SSH
        v
  Netopeer2
        |
        v
  Sysrepo
        |
        v
  allrun51
```

Cisco YANG Suite is an external validation tool. It is not part of the `allrun51` runtime, is not required for pytest, and does not change the GREEN YANG schemas. No Docker or container runtime was used.

## Observed installation

- WSL distribution: Ubuntu-22.04, WSL 2.
- Python: 3.10.12; selected because the stable YANG Suite release supports it.
- Installation home: `/home/emile/tools/yangsuite/` with `.venv`, `data`, `logs`, `config`, and `cache/pip` directories.
- YANG Suite: 3.0.14.
- Plugins: `yangsuite-netconf` 1.17.27, `yangsuite-devices` 2.9.16, `yangsuite-filemanager` 1.9.13, and `yangsuite-yangtree` 2.1.12.
- The launch scripts configure port 8480 with only the `localhost` allowed-host entry. This YANG Suite release binds to `0.0.0.0` when multiple allowed hosts are configured, so do not add `127.0.0.1` as a second entry.
- The YANG Suite URL returned HTTP 200 on 2026-11-02. NETCONF connection, server hello, module list, and XML evidence remain unvalidated.

See [version-report.txt](version-report.txt), [requirements.lock.txt](requirements.lock.txt), and [apt-packages.txt](apt-packages.txt) for the limits of the captured environment record.

## Recovery and resume

1. If WSL again reports a read-only mount or I/O error, stop writes and back up the Ubuntu VHDX before attempting filesystem repair; do not unregister the distribution.
2. From the repository root, run `bash validation/yangsuite/scripts/check_yangsuite.sh` and `bash validation/yangsuite/scripts/check_netopeer2.sh`.
3. Continue the NETCONF/YANG checks documented in the remaining files. Capture only sanitized XML under `evidence/` and generated client code under `generated/`.

The current endpoint expectation is `127.0.0.1:830`, but the listener was not rechecked after the WSL failure. No credentials are recorded here. Keep any credentials in the YANG Suite local configuration only.

## Protected scope

No files under `allrun51/` were changed by this task. Its existing worktree changes, including the untracked `src/green/markdown_tables.py`, were present before this installation work and have been left untouched.