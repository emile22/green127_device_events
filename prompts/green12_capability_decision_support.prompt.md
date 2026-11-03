# green12 — Capability-aware GREEN decision support using relationships and transition times

## Objective

Build a runnable read-only decision-support layer under:

```text
caprun12/
```

using the external NETCONF view proven by `caprun11/`.

The purpose is to answer:

```text
What Power States does this Component support?
What would the static planning saving be?
How long might recovery take?
What GREEN dependencies are relevant?
Is there enough information to recommend this state?
```

Do not perform device control.

## Read-only baselines

Use as read-only:

```text
allrun5/
ctrlrun6/
ctrlrun7/
gaprun8/
caprun10/
caprun11/
```

Do not modify them.

## Mandatory executable code

Create runnable code under `caprun12/`.

Do not stop after writing Markdown analysis.

The implementation must execute recommendations against live NETCONF data or deterministic NETCONF fixtures.

## Input architecture

The production path should obtain device information through the same external NETCONF collection path as `caprun11`.

Do not read simulator internals.

You may reuse/copy stable controller code into `caprun12/`, but previous directories remain read-only.

## Decision dimensions

Keep these independent:

```text
CAPABILITY
DEPENDENCY
TRANSITION
POLICY
OBSERVABILITY
RECOMMENDATION
```

Do not collapse them into one Boolean.

Suggested values:

```text
capability:
  SUPPORTED
  UNSUPPORTED
  UNKNOWN

dependency:
  CLEAR
  BLOCKED
  UNKNOWN

transition:
  ACCEPTABLE
  TOO_SLOW
  UNKNOWN

policy:
  ALLOWED
  FORBIDDEN
  UNKNOWN

recommendation:
  CANDIDATE
  DO_NOT_SELECT
  INSUFFICIENT_INFORMATION
```

The exact names may be adjusted, but the semantic distinctions are mandatory.

## Controller policy input

Policy is controller-local metadata, not device YANG capability.

Provide a small explicit policy file under:

```text
caprun12/config/
```

with values such as:

```text
max_restore_ms
critical_components
protected_components
minimum_required_capacity
```

Keep policy visibly separate from YANG-derived facts.

## Transition-time rule

For a low-power state:

- use `max-exit-time` when comparing against a hard restoration threshold;
- if `max-exit-time` is absent, transition acceptability is UNKNOWN unless an explicitly documented policy allows another interpretation;
- use entry time when assessing short idle windows if an idle-window input is available;
- do not invent direct low-power-to-low-power transition times.

Example:

```text
max-exit-time = 2000 ms
policy max_restore_ms = 500 ms
=> transition = TOO_SLOW
```

## GREEN relationship reasoning

Consume the existing directional Energy Object relationships from
`draft-ietf-green-power-and-energy-yang-04`.

Especially process:

```text
enabling
enabled-by
```

Do not convert them to another relationship family.

Preserve raw direction.

A Component that is enabling another Component has a functional dependency.

However, a relationship alone does not prove that the dependent Component is idle.

Therefore:

```text
known active dependent
    -> BLOCKED

explicitly known idle/inactive dependent
    -> may contribute to CLEAR

dependency exists but activity/idle status is not represented
    -> UNKNOWN
```

Never infer `CLEAR` merely from missing telemetry.

## Capability + relationship example

For a SerDes-like case:

```text
serdes-0
  supports SLEEP
  PSP = 4 W
  ENABLING -> port-a
  ENABLING -> port-b
```

The controller must distinguish:

```text
sleep-capable = yes
```

from:

```text
eligible-to-sleep = not established
```

unless the dependent states and policy provide enough evidence.

## Power State / current-state comparison

Use GREEN live operational state:

```text
power-state/oper
```

as observed truth.

Do not use `admin` as observed truth.

If admin and oper differ, report transition/in-progress state separately.

## Static versus measured values

Keep:

```text
capability nominal Power
capability max Power
GREEN instantaneous measured Power
GREEN nameplate Power
```

as distinct quantities.

A useful report may show all of them side by side, but must not merge them.

## Planning savings

Compute static PSP from capability data only.

Optionally compute a separately named observed comparison such as:

```text
measured-vs-nominal delta
```

but never call it static PSP.

## Coverage-aware recommendations

A recommendation must expose the evidence status.

Examples:

```text
CANDIDATE
  reason:
    sleep state supported
    static PSP known
    max exit time within policy
    dependency status clear

INSUFFICIENT_INFORMATION
  reason:
    dependent activity unknown

DO_NOT_SELECT
  reason:
    max exit time exceeds restoration policy
```

Unknown information must remain visible.

## UC demonstrations

Demonstrate the capability-aware reasoning against at least these GREEN use cases when available in the baseline:

- UC 2.1 — Incremental Application of the GREEN Framework
- UC 2.9 — WLAN Network Energy Saving
- UC 2.10 — Fixed Network Energy Saving
- UC 2.14 — Energy Efficiency Under Power Shortage
- UC 2.16 — Network-level Cross Layer Energy Saving

At first mention in every report section, print the full UC name.

Do not invent UC facts that are not represented by the simulator or the drafts.

## Human-readable view

Provide output such as:

```text
CAPABILITY-AWARE DECISION

Component: linecard-3
Current oper: ON

Target: SLEEP
  Capability: SUPPORTED
  Nominal ON: 200 W
  Nominal SLEEP: 15 W
  Static PSP: 185 W
  Max exit: 2000 ms
  Policy max restore: 3000 ms
  Transition: ACCEPTABLE
  Dependencies: UNKNOWN
  Recommendation: INSUFFICIENT_INFORMATION
  Reason: dependent-idle state is not available
```

## Tests

Tests must cover:

- capability-supported state;
- unsupported state;
- unknown capability;
- missing nominal Power;
- static PSP;
- max-exit threshold;
- missing transition time;
- enabling dependency;
- blocked dependency;
- unknown dependency;
- admin != oper;
- policy kept separate from YANG facts;
- no `<edit-config>`;
- previous directories unchanged.

## Required execution

Provide a clean command path, for example:

```powershell
cd caprun12
python -m green_capability_reasoner --once
python -m green_capability_reasoner --watch --interval 1
python -m green_capability_reasoner --once --show-evidence
pytest -v
```

Use repo conventions if different.

## Mandatory documentation

Create:

```text
caprun12/docs/capability_decision_matrix.md
caprun12/docs/ietf_feedback.md
caprun12/docs/unknown_information.md
```

`ietf_feedback.md` should record implementation observations relevant to:

- `draft-claise-green-capability-discovery-03`;
- `draft-ietf-green-power-and-energy-yang-04`;
- RFC 9196 integration;
- relationship/dependency sufficiency;
- transition-time sufficiency;
- component correlation.

Do not claim a confirmed YANG gap unless a separate authorized gap-analysis task establishes one.

## Out of scope

Do not:

- write `power-state/admin`;
- execute `<edit-config>`;
- execute an energy-saving action;
- change upstream YANG;
- implement IGP/TE advertisement;
- call a Component eligible merely because it is capable.

## Final report

Report:

- files created;
- commands run;
- tests;
- components evaluated;
- candidate recommendations;
- blocked recommendations;
- insufficient-information cases;
- exact evidence used for each;
- IETF feedback observations.
