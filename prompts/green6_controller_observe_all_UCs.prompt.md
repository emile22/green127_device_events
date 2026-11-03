# green6 — GREEN Controller Observation of All Event-Ready Use Cases

Act as a senior IETF GREEN, NETCONF, YANG, Sysrepo, Netopeer2, WSL, and Python controller implementation engineer.

Work in the currently opened local `green` repository.

## Baseline

Use as read-only references:

```text
green5_netconf_all_UCs.prompt
allrun5/
```

Do not modify `allrun5/`.

All output for this step MUST be under:

```text
ctrlrun6/
```

## Purpose

Build the first GREEN Controller layer that OBSERVES the existing `allrun5` device simulator through NETCONF and creates a controller-side inventory and energy view.

This step is strictly observational.

It MUST NOT:

```text
identify or classify YANG gaps
assign GAP IDs
propose YANG changes
add YANG modules
add augments
add leaves
add identities
add operational state
add configuration intent
modify upstream YANG
```

If information required by a use case is not represented in current YANG data, classify it only as:

```text
YANG-visible
derived-from-YANG
controller-metadata-only
unavailable
```

Do not decide whether this is a YANG modeling problem. That analysis is deferred to `green8_yang_gap_analysis_all_UCs.prompt`.


## Implementation is mandatory — do not stop at analysis

This prompt is an IMPLEMENTATION task, not a documentation-only review.

After inspecting `allrun5/`, you MUST create executable Python code under `ctrlrun6/`.

A response that only analyzes previous outputs, writes Markdown, or proposes an architecture is incomplete.

Even if the live NETCONF server is temporarily unavailable, still implement the controller code and unit tests using deterministic saved/fixture replies, then report the live integration blocker separately.

Create or adapt at least this executable structure, following repository conventions where they already exist:

```text
ctrlrun6/
  pyproject.toml
  src/
    green_controller/
      __init__.py
      __main__.py
      cli.py
      netconf_client.py
      collector.py
      models.py
      normalize.py
      relationships.py
      diff.py
      render.py
  tests/
  docs/
  logs/
```

The actual implementation may merge files when simpler, but MUST contain executable controller logic, not placeholders.

The controller MUST be runnable from `ctrlrun6/` with:

```powershell
py run.py
py run.py --once
py run.py --watch --interval 1
py run.py --help
python -m green_controller --once
```

Also provide:

```powershell
python -m green_controller --watch --interval 1
python -m green_controller --help
pytest -v
```

Also support launching from the repository root with `py .\ctrlrun6\run.py` and its forwarded arguments, including `py .\ctrlrun6\run.py --watch --interval 1`. Resolve the project directory, `.venv`, and package source relative to `run.py`, not the caller's current directory.

Required behavior:

- `--once` performs one real NETCONF collection cycle and prints the controller summary;
- `--watch` repeatedly collects and prints changes until interrupted;
- `run.py` with no arguments defaults to `--once`;
- if `ctrlrun6/.venv` exists, `run.py` re-launches with that project-local interpreter even when another venv is active, whether invoked inside `ctrlrun6/` or from the repository root;
- connection settings load by default from `install/runtime/netconf/connection.env`, then `allrun5/runtime/netconf/connection.env`; explicit `NETCONF_HOST`, `NETCONF_PORT`, `NETCONF_USERNAME`, and `NETCONF_PASSWORD` process environment variables override the files;
- no credentials are hard-coded;
- `--once` prints an introductory line distinguishing event labels from NETCONF data, then prints a flushed `[n/61]` UC/event progress line after each successful `<get>`;
- the event ID/name comes from `allrun5/docs/event_catalog.md`; the actual hardware and Energy Object data is fetched through NETCONF and MUST NOT be claimed to contain that event identity;
- `--watch` prints the initial summary, then only non-empty diffs; unchanged polls are silent; pressing `q` exits cleanly, and Ctrl+C exits without traceback;
- if NETCONF is unavailable, return a clear non-zero error for live mode while unit tests remain runnable from fixtures.

Before finishing this step, actually run the commands that are possible in the current environment and report their exact output/status.

## Use-case scope

Observe all Group A use cases from `allrun5`:

- UC 2.1 — Incremental Application of the GREEN Framework
- UC 2.2 — Selective reduction of energy consumption in network parts proportional to traffic levels
- UC 2.5 — Indirect Energy Monitoring and control
- UC 2.6 — Consideration of other domains for obtention of end-to-end metrics
- UC 2.7 — Dynamic adjustment of network element throughput according to traffic levels in wireless transport networks
- UC 2.8 — Video streaming use case
- UC 2.9 — WLAN Network Energy Saving
- UC 2.10 — Fixed Network Energy Saving
- UC 2.11 — Energy Efficiency Network Management
- UC 2.12 — ISAC-enabled Energy-Aware Smart City Traffic Management
- UC 2.13 — Double Accounting Open issue
- UC 2.14 — Energy Efficiency Under Power Shortage
- UC 2.15 — Energy-Efficient Management of Distributed AI Training Workloads
- UC 2.16 — Network-level Cross Layer Energy Saving

Keep Group B deferred:

- UC 2.3 — Reporting on Lifecycle Management
- UC 2.4 — Real-time Energy Metering of Virtualised or Cloud-native Network Functions

## Architecture

Implement:

```text
allrun1 GREEN device simulator
        |
        | NETCONF <get>
        v
     ncclient
        |
        v
GREEN Controller collector
        |
        +--> raw snapshot store
        +--> normalized hardware inventory
        +--> normalized Energy Object view
        +--> directional relationship graph
        +--> controller summary
```

For `--watch`, the q-key check MUST be responsive during the polling interval and MUST work from an interactive Windows terminal without requiring the user to enter a line.

The controller MUST obtain device state through NETCONF. Do not import simulator internals to bypass NETCONF.

## Collection

Retrieve at least:

```text
ietf-hardware
ietf-power-and-energy
```

and any already-present controller/network modules that can be consumed without schema changes.

Preserve for each collected value:

```text
device
retrieval time
module
data path
raw value
normalized value
```

Preserve raw XML and normalized JSON.

## Identifier discipline

Keep distinct:

```text
device ID
Energy Object ID
hardware component name
hardware UUID
relationship peer ID
controller-local object ID
```

Use `source-component-id` only according to the actual YANG schema.

Do not infer hardware hierarchy from names.

## Relationship graph

Observe and render all four directional relationship families:

```text
metering / metered-by
aggregating / aggregated-by
powering / powered-by
enabling / enabled-by
```

Preserve exact identityref direction.

Do not silently synthesize inverse relationships.

A derived inverse may be shown only if explicitly marked `[derived view]`.

## Views

Provide at least:

```text
summary
inventory
energy-objects
relationships
raw-json
raw-xml
diff
```

## Event synchronization

For every Group A event:

1. record the UC number and full UC name;
2. record the event ID and event name;
3. issue NETCONF `<get>`;
4. store raw reply;
5. update normalized controller state;
6. compute a diff against the previous observation;
7. classify each important datum as YANG-visible, derived-from-YANG, controller-metadata-only, or unavailable.

Do not interpret these classifications as YANG gaps.

## Observation catalog

Create:

```text
ctrlrun6/docs/observation_catalog.md
```

For every UC/event record:

```text
UC number and full name
event ID
observed requirement
YANG module/path if visible
classification
controller metadata if any
notes
```

Do not add a `gap` column.

## Tests

At minimum test:

- NETCONF connection;
- observation of all Group A events;
- raw XML/JSON retention;
- identifier separation;
- relationship direction;
- diff behavior;
- data classification;
- absent telemetry never becomes zero;
- `allrun5/` remains unchanged;
- no new or modified YANG schema is introduced.

## Acceptance criteria

This step is complete when:

- `ctrlrun6/` contains executable Python controller code, not only analysis/documents;
- `python -m green_controller --once` is the defined primary launch command;
- `py run.py` defaults to one NETCONF collection run and `py run.py --watch --interval 1` is the interactive watch command;
- local credential-file discovery and environment-variable overrides work without printing credentials;
- one-shot mode explains catalog labels versus NETCONF data and reports progress per GET;
- watch mode accepts `q` and suppresses empty diffs;
- `python -m green_controller --help` works;
- unit tests run even when live NETCONF is unavailable;
- `ctrlrun6/` contains a working read-only GREEN Controller observer;
- all Group A use cases are observed;
- all four relationship families are represented directionally;
- raw and normalized data are retained;
- controller diffs work;
- observations are classified without declaring YANG gaps;
- no YANG change is made;
- `allrun5/` remains unchanged.

Stop here.

Do not perform YANG gap analysis in this step.
