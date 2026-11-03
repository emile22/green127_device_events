# green7 — GREEN Controller Processing, Aggregation, Audit and Decision Preparation

Act as a senior IETF GREEN controller, YANG, NETCONF, topology, telemetry, and Python implementation engineer.

Work in the currently opened local `green` repository.

## Baselines

Use as read-only references:

```text
green5_netconf_all_UCs.prompt
allrun5/
ctrlrun6/
```

Do not modify them.

All output for this step MUST be under:

```text
ctrlrun7/
```

## Purpose

Extend the GREEN Controller from observation into processing, aggregation, audit/provenance, and deterministic decision preparation across all Group A use cases.

This step still MUST NOT perform YANG gap analysis.

It MUST NOT:

```text
declare a YANG gap
assign GAP IDs
propose YANG syntax
add YANG modules
add augments
add leaves
add identities
add state nodes
add configuration intent
modify upstream YANG
```

Any information that cannot currently be represented in YANG remains controller metadata or unavailable.

The decision about whether this constitutes a YANG gap is deferred exclusively to `green8_yang_gap_analysis_all_UCs.prompt`.


## Implementation is mandatory — build runnable controller code

This prompt MUST produce executable code under `ctrlrun7/`.

Do not satisfy the task by only reading `ctrlrun6`, analyzing its reports, or generating Markdown.

Start from the working code/behavior of `ctrlrun6`, copy/adapt what is needed into `ctrlrun7`, and implement the processing pipeline in code. `ctrlrun6/` remains read-only.

Create or adapt at least:

```text
ctrlrun7/
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
      processing.py
      aggregation.py
      provenance.py
      decisions.py
      diff.py
      render.py
  tests/
  docs/
```

The exact split may be simplified, but filtering, transformation, aggregation, provenance and recommendation logic MUST exist as executable Python, not prose-only descriptions.

Primary commands from `ctrlrun7/`:

```powershell
py run.py
py run.py --once
py run.py --watch --interval 1
py run.py --once --show-processing
py run.py --help
python -m green_controller --once
python -m green_controller --watch --interval 1
python -m green_controller --once --show-processing
python -m green_controller --help
pytest -v
```

Also support launching from the repository root with `py .\ctrlrun7\run.py` and forwarded arguments, including `py .\ctrlrun7\run.py --watch --interval 1`. Resolve the project directory, `.venv`, and package source relative to `run.py`, not the caller's current directory.

For `--once`, print at minimum:

```text
collected observations
normalized Energy Objects
relationship-derived context
derived/aggregated values
provenance summary
UC-specific recommendation
representation coverage
```

If live NETCONF is unavailable, still implement and test processing using deterministic captured/fixture replies. Do not use infrastructure unavailability as a reason to stop at analysis.

Runtime launch behavior:

- `run.py` with no arguments defaults to `--once`.
- If `ctrlrun7/.venv` exists, `run.py` re-launches with that project-local interpreter even when another venv is active, whether invoked inside `ctrlrun7/` or from the repository root.
- Load connection settings from `install/runtime/netconf/connection.env`, then `allrun5/runtime/netconf/connection.env`; explicit `NETCONF_*` environment values override the files. Never print or hard-code credentials.
- Before collecting, print a short intro that processing uses the current NETCONF snapshot and simulator event identity may not be present in device YANG.
- In `--watch`, print the initial processing view, then only non-empty changes. Pressing `q` during the polling interval exits cleanly; Ctrl+C also exits without traceback.

Before finishing, run all commands possible in the current environment and report exact results.

## Use-case scope

Process all Group A use cases:

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
allrun1 devices
     |
     | NETCONF
     v
collector
     |
     v
normalized observations
     |
     +--> filtering
     +--> transformation
     +--> aggregation
     +--> relationship traversal
     +--> network energy view
     +--> audit/provenance
     +--> decision preparation
     |
     v
controller recommendation / intended action
```

The controller remains read-only toward devices.

Do NOT send `<edit-config>`.

## Processing functions

Implement where meaningful:

```text
sum
average
peak
minimum
delta
rate/trend
coverage
completeness
de-duplication
relationship traversal
source classification
measurement / estimate / derived classification
```

Do not combine incompatible units or incompatible measurement intervals.

## Provenance

For every derived value retain:

```text
contributing device values
source YANG paths
relationship edges used
transformation applied
event that produced the value
measured / estimated / derived / incomplete status
```

If provenance cannot be represented by existing YANG, keep it as controller metadata. Do not call this a gap yet.

## Network energy view

Build a controller-side view across devices and components.

For every field classify:

```text
YANG-backed
derived-from-YANG
controller-metadata-only
unavailable
```

No new YANG is allowed.

## Deterministic recommendation per UC

For every Group A use case produce at least one deterministic recommendation tied to the UC semantics.

Examples:

- UC 2.2 — Selective reduction of energy consumption in network parts proportional to traffic levels: recommend concentration of traffic and low-power eligibility.
- UC 2.5 — Indirect Energy Monitoring and control: select the external meter as the authoritative observation source for an uninstrumented target.
- UC 2.9 — WLAN Network Energy Saving: recommend the next AP power mode based on traffic and functional constraints.
- UC 2.10 — Fixed Network Energy Saving: recommend sleep/wake based on observed load.
- UC 2.13 — Double Accounting Open issue: mark an accounting total authoritative only when topology is complete.
- UC 2.14 — Energy Efficiency Under Power Shortage: preserve essential service and reduce non-critical consumption.
- UC 2.16 — Network-level Cross Layer Energy Saving: coordinate overlay and underlay dependencies before recommending low-power transition.

Do not execute recommendations on devices.

## Coverage evidence

Create:

```text
ctrlrun7/docs/representation_coverage.md
```

For each meaningful controller requirement record:

```text
UC number and full UC name
event ID
controller function
required semantic information
existing module/path if any
coverage: complete / partial / absent / ambiguous
controller workaround
operational impact
```

`partial`, `absent`, or `ambiguous` are coverage observations only.

Do not call them YANG gaps.

Do not assign GAP IDs.

## Requirement matrix

Create:

```text
ctrlrun7/docs/requirement_to_yang_coverage.md
```

Columns:

```text
UC and full name
event
requirement
scope: device/controller
existing module
existing path
coverage
metadata workaround
impact
```

No GAP-ID column.

## green8 handoff

Generate:

```text
ctrlrun7/docs/green8_input.json
```

For every requirement with `partial`, `absent`, or `ambiguous` coverage include:

```text
UC number
UC full name
event_ids
requirement
scope
searched_modules
searched_paths
coverage
workaround
impact
example_runtime_value
```

Do NOT include:

```text
gap_id
gap classification
proposed YANG syntax
proposed leaf name
proposed augment
```

`green8_yang_gap_analysis_all_UCs.prompt` will decide whether any of these are actual YANG gaps.

## Tests

Test:

- all Group A processing paths;
- derived values retain provenance;
- relationship traversal remains directional;
- double-accounting protection remains topology-driven;
- missing/incomplete data never becomes zero;
- units and intervals are checked;
- every Group A UC produces a deterministic recommendation;
- recommendations do not perform device control;
- coverage evidence is generated;
- no GAP IDs exist;
- no YANG changes are made;
- `ctrlrun6/` and `allrun5/` remain unchanged.

## Acceptance criteria

This step is complete when:

- `ctrlrun7/` contains executable controller-processing Python code, not only reports;
- `py run.py` defaults to one processing cycle and selects the local venv when present;
- local connection-file discovery and environment overrides work without printing credentials;
- the processing intro explains the current NETCONF snapshot/event-identity boundary;
- watch mode accepts `q` and does not repeat unchanged processing output;
- `python -m green_controller --once` is runnable from `ctrlrun7/`;
- processing, aggregation, provenance, and recommendations are implemented in code and covered by tests;
- controller processing works for every Group A use case;
- filtering/transformation/aggregation/audit/decision-preparation are exercised where meaningful;
- every derived result has provenance;
- representation coverage is documented;
- `green8_input.json` is complete;
- no requirement is labeled a YANG gap;
- no GAP IDs are assigned;
- no device control is performed;
- no YANG modification or extension exists.

Stop here.

YANG gap analysis is reserved exclusively for green8.
