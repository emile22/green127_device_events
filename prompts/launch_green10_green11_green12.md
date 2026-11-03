# Launch green10, green11 and green12 sequentially

Run these three implementation prompts sequentially in the same task:

1. `/green10_capability_device_netconf`
   using `green10_capability_device_netconf.prompt.md`

2. `/green11_capability_controller_join`
   using `green11_capability_controller_join.prompt.md`

3. `/green12_capability_decision_support`
   using `green12_capability_decision_support.prompt.md`

These are implementation tasks, not analysis-only tasks.

## Global rules

- Inspect the current repo and existing working code first.
- `allrun5/`, `ctrlrun6/`, `ctrlrun7/`, and `gaprun8/` are read-only.
- When moving to the next step, the previous capability run becomes read-only.
- Use no containers.
- Preserve Windows Python/ncclient + native Ubuntu/WSL Sysrepo/Netopeer2.
- Use the actual YANG schemas as authoritative when draft prose conflicts with schema.
- Use `draft-claise-green-capability-discovery-03`, not an older revision.
- Do not silently change upstream IETF YANG.
- Missing information is UNKNOWN, never zero.
- Do not perform NETCONF device control in these three steps.

## Step 1 — green10

Implement the device-side Power State capability model under:

```text
caprun10/
```

The implementation MUST:

- install/use the exact capability YANG;
- expose RFC 9196 system capabilities as operational data through Sysrepo/Netopeer2;
- bind per-Component capability entries to real RFC 8348 hardware Components;
- verify the result through NETCONF;
- provide runnable code and tests.

Do not stop after writing YANG files or Markdown.

Run the implementation and tests.

Only continue when `caprun10/` is sufficiently complete to supply real or fixture-validated NETCONF capability data.

## Step 2 — green11

Use `caprun10/` as read-only.

Implement the external capability-aware controller under:

```text
caprun11/
```

The live controller must use NETCONF only for device truth.

It MUST join:

```text
RFC 8348 hardware
+
RFC 9196 / ietf-power-state-capabilities
+
ietf-power-and-energy live state
```

by the RFC 8348 hardware Component.

It MUST implement:

- RFC 9196 precedence;
- system-wide fallback;
- UNKNOWN coverage;
- sleep-capable derivation;
- static PSP;
- nameplate consistency checks;
- raw NETCONF snapshots;
- tests.

Run the controller and tests before continuing.

## Step 3 — green12

Use `caprun10/` and `caprun11/` as read-only.

Implement capability-aware decision support under:

```text
caprun12/
```

It MUST combine:

```text
Power State capability
+
live oper state
+
transition times
+
GREEN enabling/enabled-by relationships
+
explicit controller policy
```

while keeping those semantic layers separate.

It MUST produce evidence-based recommendations only.

It MUST NOT execute `<edit-config>` or change `power-state/admin`.

Run the implementation and tests.

## Important correlation rule

For the current YANG schema, correlate through:

```text
RFC9196 node-selector
  -> /ietf-hardware:hardware/component[name='X']

ietf-power-and-energy source-component-id
  -> /ietf-hardware:hardware/component/name
```

Do not replace this with UUID because of prose in `draft-ietf-green-power-and-energy-yang-04`.

Keep hardware name and UUID as separate fields.

## Required final report

At the end provide one consolidated report with:

- files created in `caprun10/`, `caprun11/`, and `caprun12/`;
- exact YANG modules and revisions;
- exact commands run;
- NETCONF operations used;
- test results;
- capability coverage;
- system-wide fallback cases;
- unknown capability cases;
- Component join results;
- static PSP calculations;
- transition-time checks;
- dependency reasoning results;
- recommendations;
- observations useful for the GREEN WG;
- remaining blockers.

If one step has a genuine blocking failure, stop before the dependent step and report the exact blocker instead of fabricating outputs.
