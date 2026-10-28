Act as a senior network-management and YANG implementation engineer. Build a runnable reference implementation of a GREEN energy-management controller and a managed-device simulator in this repository.

First inspect the repository and its instructions. Preserve existing work and conventions. If the repository is empty, choose a minimal, maintainable stack and document the choice. Before implementation, summarize the architecture and identify any specification gaps that affect behavior. Then implement the system, tests, and setup documentation; do not stop at a proposal.

Normative and design references:
- Power and Energy YANG Module, draft-ietf-green-power-and-energy-yang-04:
  https://datatracker.ietf.org/doc/html/draft-ietf-green-power-and-energy-yang-04
- GREEN Framework, draft-ietf-green-framework-02:
  https://datatracker.ietf.org/doc/html/draft-ietf-green-framework-02
- GREEN Use Cases, draft-ietf-green-use-cases-02:
  https://datatracker.ietf.org/doc/html/draft-ietf-green-use-cases-02
- GREEN Controller YANG, draft-swepcarl-green-controller-yang-00:
  https://datatracker.ietf.org/doc/html/draft-swepcarl-green-controller-yang-00
- Power State Capability Discovery, draft-claise-green-capability-discovery-02:
  https://datatracker.ietf.org/doc/html/draft-claise-green-capability-discovery-02
- Hardware inventory: RFC 8348; YANG Push: RFC 8641; NACM: RFC 8341.

Treat all Internet-Drafts as evolving work, not finalized standards. Read the actual YANG modules and relevant sections before coding. Record which draft/version each implemented behavior follows.

Architecture and responsibilities:

1. Device
- Implement a device adapter or simulator that exposes the `ietf-power-and-energy` model from draft -04, including operational `energy-objects` and writable `energy-control`.
- Represent a device and its components using the RFC 8348 hardware hierarchy. Correlate energy objects with hardware components using the model’s component reference; preserve stable UUID mappings where available.
- Populate realistic, deterministic sample data for instantaneous power, cumulative consumed/delivered energy, power state, measurement locality, accuracy identity, certifications, and read-only relationships.
- Permit power-state requests only through `energy-control/.../power-state/admin`. Track requested `admin` separately from actual operational `oper`; simulate transitions instead of reporting a requested state as already achieved.
- Include a controllable measurement provider so tests and demos can change readings and simulate missing sensors, stale data, and device errors.

2. Controller
- Discover/onboard devices, retrieve hardware inventory, energy telemetry, and advertised power-state capabilities, and correlate them in a controller inventory.
- Collect telemetry using YANG Push where supported. Provide a polling fallback and make collection status and freshness visible.
- Keep controller orchestration separate from device-owned state. A controller-side energy network view may follow the structures in controller draft -00 (`ietf-power-energy-network`), but mark its draft status and avoid claiming that its incomplete collection configuration or audit sections are standardized.
- Provide an operator-facing API or CLI to list devices/components and their power, energy, accuracy, capabilities, and state; request a supported state transition; and inspect the transition result and collection errors.
- Model energy relationships and use metering/aggregation relationships to avoid double counting. Keep consumed energy distinct from delivered energy.
- If capability discovery draft -02 is implemented, keep its static supported-state data separate from live operational state. Reuse its `ietf-power-state-capabilities` schema and power-state identities; include nominal/max power and transition times when available. Missing capability data means “unknown,” not zero or unsupported.

Safety, correctness, and security:
- Do not invent RPCs, notifications, identities, or YANG nodes and present them as defined by draft -04. The draft explicitly defines no RPC operations or YANG notifications. Use protocol operations supported by the chosen management stack; describe any implementation-specific extensions as such.
- Before a state change, check that the target component advertises the requested state when capability data is available. Enforce configurable safety rules, transition limits, cooldown/rate limits, operator authorization, and dependency checks. Default to dry-run or explicit operator confirmation for disruptive actions; never silently power off a component.
- Restrict control writes and sensitive telemetry reads. Use authenticated, encrypted management connections and apply least privilege. Do not commit credentials; use environment variables or local secret configuration.
- Preserve and report measurement accuracy and source provenance. Do not silently aggregate readings with incompatible units or accuracy.
- Check draft text for conflicting units, descriptions, or references. Document discrepancies and choose one explicit interpretation for the demo rather than silently “correcting” the draft.

Validation and deliverables:
- Validate YANG modules with appropriate YANG tooling and validate sample instance data against them.
- Add unit tests for parsing/mapping, component identity correlation, unit handling, accuracy inheritance, aggregation/double-counting prevention, unsupported or unsafe state requests, and transition behavior.
- Add an end-to-end test that starts the device simulator and controller, discovers a device, collects telemetry, requests a state transition, and observes the resulting operational state.
- Include a README with architecture, draft-to-implementation mapping, security assumptions, limitations, setup/run/test commands, and a sample walkthrough.
- Run the focused tests and YANG validation. Report exact commands and results, plus any behavior that remains a draft interpretation or is not implemented.
