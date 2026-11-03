# Launch Cisco YANG Suite WSL installation and GREEN validation

Run the instructions in:

```text
yangsuite_wsl_install.prompt.md
```

against the currently opened `green` repository.

## Execution rules

- install Cisco YANG Suite natively under Ubuntu/WSL with Python;
- do not use Docker or containers;
- keep the YANG Suite environment isolated under:

```text
~/tools/yangsuite/
```

- keep all repository-side scripts, lock files, reports, and validation evidence under:

```text
validation/yangsuite/
```

- do not modify:

```text
allrun51/
```

- use the existing Netopeer2/Sysrepo stack as the NETCONF target;
- inspect the actual environment and package versions before installing anything;
- use stable package versions, not pre-releases, unless the stable release cannot provide the required NETCONF functionality;
- determine whether the installed YANG Suite NETCONF path depends on `ncclient`;
- configure YANG Suite for local browser access, preferably:

```text
http://localhost:8480
```

- validate:
  - NETCONF `<hello>`;
  - YANG module discovery;
  - `ietf-hardware`;
  - `ietf-power-and-energy`;
  - full `<get>`;
  - subtree-filtered `<get>`;
  - Energy Objects;
  - `source-component-id`;
  - all four GREEN relationship families;
  - event-to-event changes;
  - UC 2.13 observability behavior;
- freeze the working Python environment;
- do not store credentials or secrets in the repository;
- do not stop after planning: perform the installation, validation, and documentation requested by the prompt;
- do not claim success for commands or GUI checks that were not actually completed.

## Final report

At the end, report:

```text
WSL distribution
Python version
YANG Suite version
YANG Suite NETCONF plugin version
whether ncclient is in the NETCONF dependency path

YANG Suite URL
NETCONF target host/port
NETCONF connection result

server advertised module count
ietf-hardware revision
ietf-power-and-energy revision

full <get> result
subtree <get> result
Energy Object validation result
relationship validation result
event-transition result
UC 2.13 result

files created under validation/yangsuite
confirmation that allrun51 was not modified
remaining blockers
```

Do not fabricate results.
