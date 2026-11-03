# green8 — YANG Gap Analysis and Experimental Model Augmentation for All GREEN Use Cases

Act as a senior IETF YANG model designer, GREEN architecture engineer, NETCONF implementer, and interoperability reviewer.

Work in the currently opened local `green` repository.

## Baselines

Use as read-only evidence:

```text
green5_netconf_all_UCs.prompt
allrun5/
ctrlrun6/
ctrlrun7/
ctrlrun7/docs/green8_input.json
```

Do not modify previous run directories.

All output MUST be under:

```text
gaprun8/
```

## Purpose

THIS is the first step in this sequence authorized to:

```text
identify confirmed YANG gaps
assign GAP IDs
propose YANG model changes
add experimental YANG
add leaves
add state
add configuration intent
add identities
add containers/lists
add augments
```

Do not assume that every `partial`, `absent`, or `ambiguous` observation from green7 is a YANG gap.

Each candidate must first be checked against the actual YANG corpus.


## Implementation is mandatory — analysis must lead to validated artifacts

This step is not complete with a gap report alone.

You MUST create executable validation tooling and, for every confirmed gap that requires modeling, real experimental YANG code under `gaprun8/`.

Create or adapt at least:

```text
gaprun8/
  pyproject.toml
  src/
    green_gap_tool/
      __init__.py
      __main__.py
      analyze.py
      schema_inventory.py
      traceability.py
      validate.py
  yang/
    upstream/
    experimental/
  tests/
  docs/
```

Primary commands from `gaprun8/`:

```powershell
py run.py
py run.py analyze
py run.py validate
py run.py report
py run.py --help
python -m green_gap_tool
python -m green_gap_tool analyze
python -m green_gap_tool validate
python -m green_gap_tool report
python -m green_gap_tool --help
pytest -v
```

From the repository root, also support `py .\gaprun8\run.py` and forwarded subcommands such as `py .\gaprun8\run.py report`. Resolve the project directory, `.venv`, and package source relative to `run.py`, not the caller's current directory; use `gaprun8/.venv` when it exists.

With no subcommand, both `py run.py` and `python -m green_gap_tool` default to `analyze` and print an intro identifying `ctrlrun7/docs/green8_input.json` and the actual repository schema corpus as their inputs. `validate` prints an intro that it checks copied upstream/experimental modules and representative data. These are one-shot subcommands, not interactive watch loops; q-to-quit does not apply.

`analyze` MUST read `ctrlrun7/docs/green8_input.json`, inspect the actual schema corpus, and produce machine-readable plus human-readable decisions.

`validate` MUST run available schema/instance checks (`pyang`, and `yanglint` when available) against copied upstream and experimental modules.

For each CONFIRMED GAP that needs new modeling, create actual `.yang` content in `gaprun8/yang/experimental/`; do not leave only pseudocode in Markdown.

For each rejected candidate, create no experimental YANG node.

Keep the machine-readable decision and rationale separate: rationale text MUST NOT repeat a label such as `NOT A GAP:` or `CONFIRMED GAP:`. In `report` and generated Markdown, print the decision exactly once, followed by the explanation. Add a regression test that rejects output such as `Decision: NOT A GAP. NOT A GAP:` and regenerate the reports after changing analysis or report-generation logic.

If there are zero confirmed gaps after evidence-based analysis, it is acceptable to create no experimental nodes, but executable analysis/validation tooling and rejected-candidate evidence remain mandatory.

If Sysrepo/Netopeer2 is unavailable, still generate and validate YANG statically and run unit tests; report live NETCONF validation as blocked rather than stopping at analysis.

Before finishing, run all commands possible in the current environment and report exact results.

## Gap rule

A YANG gap exists only when:

1. a UC or controller function has a concrete semantic requirement;
2. one or more runtime events demonstrate that requirement;
3. the relevant current YANG modules have been inspected;
4. no adequate existing representation exists, or the existing representation is materially insufficient/ambiguous;
5. the problem is not merely a display preference or implementation naming difference.

## Use-case scope

Analyze all Group A use cases:

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

Also review modeling needs from Group B:

- UC 2.3 — Reporting on Lifecycle Management
- UC 2.4 — Real-time Energy Metering of Virtualised or Cloud-native Network Functions

For UC 2.3 — Reporting on Lifecycle Management and UC 2.4 — Real-time Energy Metering of Virtualised or Cloud-native Network Functions, identify modeling needs only from text actually present in the draft. Do not invent unsupported event behavior.

## YANG corpus to inspect

At minimum inspect exact repository revisions of:

```text
ietf-power-and-energy
ietf-hardware
GREEN Controller YANG modules
GREEN capability discovery YANG
GREEN provenance-related YANG if present
ietf-network
ietf-network-topology
network inventory / IVY modules used by the controller design
all imported dependencies
```

Use actual schema, not prose summaries alone.

Generate `pyang -f tree` outputs.

Use `yanglint` for instance validation when available.

## Candidate analysis

For every entry in `ctrlrun7/docs/green8_input.json`:

1. restate requirement;
2. recall the UC number and full UC name;
3. identify demonstrating events;
4. identify device/controller scope;
5. inspect existing modules and paths;
6. inspect identities, typedefs, relationships, imported models;
7. classify coverage: complete / partial / absent / ambiguous / represented elsewhere;
8. decide: NOT A GAP or CONFIRMED GAP.

Only confirmed gaps receive stable IDs:

```text
GAP-001
GAP-002
...
```

## Gap categories

Use:

```text
STATE-GAP
CONFIG-GAP
IDENTITY-GAP
RELATIONSHIP-GAP
PROVENANCE-GAP
COLLECTION-GAP
TRANSFORMATION-GAP
AGGREGATION-GAP
DELIVERY-GAP
TIMING-GAP
QUALITY-GAP
CAPABILITY-GAP
NETWORK-VIEW-GAP
LIFECYCLE-GAP
VIRTUALIZATION-GAP
OTHER-GAP
```

## Authorization to add experimental YANG

For confirmed gaps only, this step may add:

```text
leaf
leaf-list
container
list
choice/case
identity
typedef
grouping
config false operational state
config true intent
must/when constraints
augment
feature
provenance structures
```

Do NOT modify upstream IETF modules in place.

Use:

```text
gaprun8/yang/
  upstream/
  experimental/
```

Copy upstream modules unchanged into `upstream/`.

Put additions under `experimental/`.

Prefer `augment` when semantically appropriate.

Use unmistakably experimental module names such as:

```text
example-green-controller-gaps.yang
example-green-power-energy-gaps.yang
```

Do not create a local `ietf-*` module.

## State modeling

This step is explicitly authorized to add operational state when justified.

For operational state use:

```yang
config false;
```

Requirements:

- observed state remains separate from configured/requested intent;
- define units;
- define timestamp/interval semantics where relevant;
- define counter reset semantics where relevant;
- define unknown/unavailable semantics;
- never use zero as absence;
- document provenance and meaning.

Potential topics to investigate, NOT automatically add:

```text
topology completeness
accounting validity
measurement interval boundaries
last counter reset time
data coverage
baseline provenance
controller collection status
aggregation status
transformation status
delivery status
power-source availability
criticality/preservation state
cross-layer coordination state
virtualized workload attribution
lifecycle metadata freshness
```

Every addition requires a confirmed GAP ID.

## Configuration modeling

Where controller intent is genuinely missing, investigate:

```text
collection method
collection target
filter
transformation
aggregation operation
delivery destination
network-view population policy
policy for incomplete topology
energy optimization policy
```

Do not add config simply because Python exposes an internal option.

## Relationship modeling

Verify sufficiency of:

```text
metering / metered-by
aggregating / aggregated-by
powering / powered-by
enabling / enabled-by
```

Do not add new relationship identities unless a confirmed requirement cannot be represented.

Keep separate:

```text
hardware containment
Energy Object relationship
traffic topology
functional dependency topology
provenance/collection graph
```

## Provenance and audit

Determine whether existing models can represent:

```text
source device
source object
source path
collection method
collection time
transformation
aggregation operation
inputs
output
accuracy
completeness
lineage
```

Add only the minimum experimental YANG needed for confirmed gaps.

## Gap matrix

Create:

```text
gaprun8/docs/yang_gap_matrix.md
```

Use a compact summary table with these columns:

```text
UC ID only
events
Gap? (No, Yes, or Deferred)
scope
coverage before
GAP ID
```

Before the summary, include a `Use Case Names` table mapping every UC ID to its full name. Keep only the UC ID in the summary table's UC column. Do not put full requirements, long YANG paths, or rationale paragraphs into summary-table cells. Preserve the remaining fields in per-UC detail sections below the table: requirement, existing module/path (one path per line), confirmed gap, category, proposed solution, experimental module/path, config, units/type, rationale, and test. Keep Group B review details in the same readable detail-section style.

Pad Markdown table cells and separator rows to the same per-column widths so pipe separators align in the source document.

In summary rows, use `No` for NOT A GAP, `Yes` for CONFIRMED GAP, and `Deferred` for Group B candidates; retain full classifications and review explanations in detail sections and reports. Use the concise Group B coverage label `underspecified`.

## Rejected candidates

Create:

```text
gaprun8/docs/rejected_gap_candidates.md
```

Explain every candidate not confirmed as a gap.

## Before/after tree

Create:

```text
gaprun8/docs/yang_tree_before.txt
gaprun8/docs/yang_tree_after.txt
gaprun8/docs/yang_tree_diff.md
```

Every added node must be visible.

## Traceability

Every experimental YANG node MUST map to at least one GAP ID.

Every GAP ID MUST map to:

```text
UC full name
event(s)
requirement
test
```

No orphan nodes.

## Runtime and NETCONF validation

Use representative events to prove previously metadata-only information can now be represented through experimental YANG where justified.

Do not move every runtime field into YANG.

Only confirmed gaps may become YANG-backed.

Expose representative experimental operational state through Sysrepo/Netopeer2 when device-side modeling is appropriate.

If a confirmed gap is controller-side only, model/test it in the controller datastore instead of forcing it onto the device.

## Tests

At minimum test:

- upstream YANG files remain byte-for-byte unchanged;
- experimental modules pass `pyang`;
- instance data passes `yanglint` when available;
- every experimental node maps to a GAP ID;
- every GAP ID has evidence;
- rejected candidates have explanations;
- `config false` state is not writable as configuration;
- operational state is retrievable;
- units/types are enforced;
- unknown/unavailable is not zero;
- relationship semantics remain valid;
- legacy `allrun5` behavior still works;
- controller processing still works;
- experimental additions close the intended confirmed gaps.

## Required reports

Create:

```text
gaprun8/docs/confirmed_gaps.md
gaprun8/docs/rejected_gap_candidates.md
gaprun8/docs/yang_gap_matrix.md
gaprun8/docs/modeling_decisions.md
gaprun8/docs/upstream_change_proposals.md
```

Clearly distinguish:

```text
local experimental augmentation
versus
possible future IETF proposal
```

## Acceptance criteria

This step is complete when:

- `gaprun8/` contains executable gap-analysis/validation tooling, not only documents;
- `python -m green_gap_tool analyze` and `python -m green_gap_tool validate` are the defined primary commands;
- confirmed modeling gaps result in real experimental `.yang` artifacts when justified;
- all green7 coverage candidates have been checked against actual YANG;
- false candidates are rejected with evidence;
- only confirmed gaps receive GAP IDs;
- only confirmed gaps receive experimental YANG additions;
- operational state may be added with `config false`;
- missing intent may be modeled separately from state;
- upstream YANG remains unchanged;
- experimental modules validate;
- representative augmented data is retrievable where appropriate;
- use-case/event traceability is preserved;
- every addition has a GAP ID and test;
- before/after model differences are documented;
- possible upstream changes are separated from local experimental implementation.

Stop after validated experimental YANG gap closure.

Do not claim experimental modules are IETF standards.
