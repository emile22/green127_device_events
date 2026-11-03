# GREEN All Event-Ready Use Cases (`allrun5`)

`allrun5` is an isolated, read-only NETCONF simulator for the 14 event-ready GREEN use cases. It adapts the working `minrun4/` implementation as a read-only baseline; `minrun4/` itself is not part of this project's runtime or outputs. All simulator code, copied YANG, tests, scripts, generated snapshots, and logs belong under `allrun5/`.

The event meanings follow the upstream [draft-ietf-green-use-cases](https://github.com/emile22/draft-ietf-green-use-cases/blob/main/draft-ietf-green-use-cases.md). Event IDs and descriptions are simulator-specific and are not represented as standardized IETF events.

## Use-Case Groups

Group A is UC 2.1, 2.2, 2.5–2.16 excluding 2.3 and 2.4: **14 use cases, 122 deterministic events**. Each meets the doubled minimum event count. Group B contains only UC 2.3 and UC 2.4; they are deferred because their current text lacks enough operational detail for grounded event sequences. See [use_case_groups.md](docs/use_case_groups.md), [deferred_group_b.md](docs/deferred_group_b.md), and the generated [event_catalog.md](docs/event_catalog.md).

| UC | Events | UC | Events |
| --- | ---: | --- | ---: |
| UC 2.1 | 8 | UC 2.9 | 10 |
| UC 2.2 | 10 | UC 2.10 | 8 |
| UC 2.5 | 8 | UC 2.11 | 8 |
| UC 2.6 | 8 | UC 2.12 | 10 |
| UC 2.7 | 8 | UC 2.13 | 8 |
| UC 2.8 | 8 | UC 2.14 | 10 |
| UC 2.15 | 8 | UC 2.16 | 10 |

## Architecture

```text
Windows Python 3.11 runtime and ncclient
       | shared allrun5/runtime/operational.json
       v
WSL Sysrepo operational-data plugin
       v
WSL Netopeer2 on TCP/830
```

Windows runs the GREEN event simulator, adapter, CLI, and ncclient tests. Runtime snapshots and generated test credentials stay in `runtime/`; formatted/runtime and provider traces stay in `logs/`. Sysrepo stores the YANG modules and invokes the C operational-data provider. Netopeer2 serves NETCONF over SSH. WSL is used for native Sysrepo/Netopeer2 only; no containers are used. Windows tests prefer `localhost` and fall back to `NETCONF_HOST` from `runtime/netconf/connection.env` if WSL localhost forwarding is unavailable.

The YANG revisions copied unchanged from `minrun4/yang/` are:

| Module | Revision | Baseline source | allrun5 destination |
| --- | --- | --- | --- |
| `ietf-power-and-energy` | `2026-07-02` | `minrun4/yang/ietf-power-and-energy@2026-07-02.yang` | `yang/ietf-power-and-energy@2026-07-02.yang` |
| `iana-power-and-energy` | `2026-07-02` | `minrun4/yang/iana-power-and-energy@2026-07-02.yang` | `yang/iana-power-and-energy@2026-07-02.yang` |
| `ietf-hardware` | `2018-03-13` | `minrun4/yang/ietf-hardware@2018-03-13.yang` | `yang/ietf-hardware@2018-03-13.yang` |
| `iana-hardware` | `2018-03-13` | `minrun4/yang/iana-hardware@2018-03-13.yang` | `yang/iana-hardware@2018-03-13.yang` |
| `ietf-inet-types` | `2013-07-15` | `minrun4/yang/ietf-inet-types@2013-07-15.yang` | `yang/ietf-inet-types@2013-07-15.yang` |
| `ietf-yang-types` | `2013-07-15` | `minrun4/yang/ietf-yang-types@2013-07-15.yang` | `yang/ietf-yang-types@2013-07-15.yang` |

## Setup

Create a separate Windows environment from this directory:

```powershell
cd allrun5
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Install native dependencies once in the existing Ubuntu WSL distribution:

```bash
sudo apt update
sudo apt install -y sysrepo sysrepo-plugind netopeer2 libyang2-dev libyang2-tools build-essential pkg-config libssh-dev
```

From `allrun5/` in WSL, start/check the services:

```bash
bash scripts/wsl-netconf-start.sh
bash scripts/wsl-netconf-status.sh
```

The installer installs only missing YANG modules and creates an allrun5-specific smoke user. It stores connection details under `runtime/netconf/connection.env`; do not commit this file.

At launcher initialization, the compact WSL readiness display shows Sysrepo
and Netopeer2 process IDs plus explicit RFC 8348 hardware parent/sibling ties
using Energy Object IDs and `parent-rel-pos`.

## Runtime

```powershell
python run.py
```

`run.py` checks WSL health and starts the allrun5 NETCONF stack if it is stopped
or incomplete. It then runs pytest before the interactive simulator and stops
the WSL services on every exit. To keep services running after a demo, start
them with the WSL script and run `python -m green` directly.

For a noninteractive test-first run, use `python run.py --auto --interval 0`.

Controls:

| Input | Behavior |
| --- | --- |
| ENTER | Advance exactly one event. |
| `a` | Run all remaining Group A events across UC boundaries. |
| `d` | Toggle live operational-data tracing and append records under `logs/`. |
| `r` | Reset all scenario state and restart at UC 2.1 / U1-0. |
| `q` | Exit cleanly. |
| `summary` | Display hardware, energy objects, relationships, and UC interpretation. |
| `relationships` | Display the directional Energy Object graph. |
| `json` | Display normalized full YANG JSON. |
| `xml` | Fetch and display the actual NETCONF XML reply. |
| `diff` | Compare relationship and observed-state changes with the previous event. |

The default event display prints its UC/event ID and explanation, followed by
compact `HW`, `ENERGY`, `REL`, and `DIFF` lines. The `summary` command opens the
detailed hardware inventory, Energy Objects, relationships, and UC interpretation.

Every event has a deterministic explanation under 20 words. Runtime/controller metadata remains separate from YANG data. Missing measurements/capabilities remain unknown; interval and cumulative energy are distinct; cumulative counters reset only on `r`.

## Relationship Semantics

All four YANG relationship families are represented with explicit inverse identities:

- `metering` / `metered-by`: measurement topology; only this family drives accounting de-duplication.
- `aggregating` / `aggregated-by`: aggregation of Energy Management information, not traffic concentration.
- `powering` / `powered-by`: electrical supply topology.
- `enabling` / `enabled-by`: functional dependency, not electrical power flow.

Forward and inverse links are stored as distinct directional relationships. `source-component-id` maps an Energy Object to the RFC 8348 hardware component name; it is not a relationship peer or hardware UUID. Hardware containment is represented only by RFC 8348 `parent` data. The WSL installer seeds that configuration from `yang/hardware-hierarchy.xml`; it does not infer parent links from Energy Object IDs or names. See the generated [relationship_coverage.md](docs/relationship_coverage.md).

## Capability-discovery Readiness

The [capability-discovery readiness inventory](docs/capability_discovery_readiness.md) records stable RFC 8348 Component names/UUIDs, Energy Object mappings, and existing dependency relationships selected for future `caprun10+` demonstrations. This is correlation readiness only: allrun5 does not implement RFC 9196, `ietf-system-capabilities`, or `ietf-power-state-capabilities`, and UC 2.11 capability classification remains simulator/controller metadata.

## NETCONF and Services

NETCONF is read-only in this increment. The simulator drives events and Sysrepo/Netopeer2 expose the resulting operational snapshot over `<get>`. No `<edit-config>`, custom RPC, notification, YANG Push, or RESTCONF is implemented.

From WSL:

```bash
bash scripts/wsl-netconf-status.sh
bash scripts/wsl-netconf-stop.sh
bash scripts/wsl-netconf-start.sh
```

`stop` halts `sysrepo-plugind` and `netopeer2` and clears transient service environment; installed modules, host keys, allrun5 snapshots, logs, and credentials are not deleted. `start` rebuilds the provider, installs any missing modules, refreshes the local smoke credential, and restarts the services. Run live client tests from Windows:

```powershell
.\scripts\run-netconf-smoke.ps1
```

## Tests and Validation

```powershell
python -m pytest -v
python -m green --auto --interval 0
python -m green.catalog_docs
pyang -p yang yang\ietf-power-and-energy@2026-07-02.yang
```

The pytest suite includes 14 focused UC modules, deterministic runtime/accounting/adapter tests, relationship coverage/symmetry tests, and live `ncclient` NETCONF tests. `yanglint` can validate a generated operational instance from WSL:

```bash
yanglint -p yang \
  yang/iana-hardware@2018-03-13.yang \
  yang/ietf-hardware@2018-03-13.yang \
  yang/iana-power-and-energy@2026-07-02.yang \
  yang/ietf-power-and-energy@2026-07-02.yang \
  runtime/operational.json
```

The current capability is read-only operational simulation. Future work can refine Group B once its source text is more operationally specific and separately consider protected NETCONF control; neither is implemented here.
