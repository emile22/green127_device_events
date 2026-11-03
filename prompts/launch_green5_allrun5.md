# Run green5 / allrun5

Run the implementation defined in:

`green5_netconf_all_UCs.prompt.md`

This is an implementation task, not an analysis-only task.

First inspect the existing `minrun4/` implementation and use it strictly as a read-only baseline.

Then create or update the complete implementation under:

`allrun5/`

Follow the prompt exactly.

## Important execution rules

- Do not modify `minrun4/`.
- All implementation output must remain under `allrun5/`.
- Implement all 14 Group A GREEN use cases defined in the prompt.
- Keep UC 2.3 and UC 2.4 deferred.
- Preserve the existing Windows Python + WSL Sysrepo/Netopeer2 architecture.
- Do not use containers.
- Keep NETCONF read-only.
- Preserve `ENTER/a/d/r/q` runtime behavior.
- Preserve raw NETCONF XML/JSON and the human-readable summary, relationships, and diff views.
- Implement and test all four GREEN relationship families.
- Preserve stable RFC 8348 hardware component names, UUIDs, Energy Object IDs, and `source-component-id` mappings.
- Implement the new capability-discovery readiness requirements, but DO NOT implement RFC 9196 or `ietf-power-state-capabilities` in `allrun5`.
- Generate `allrun5/docs/capability_discovery_readiness.md`.
- Ensure selected future capability-demo components have stable RFC 8348 identities and hardware-backed `enabling/enabled-by` relationships where applicable.
- Keep UC 2.11 capability classification as simulator/controller metadata only.
- Do not add capability YANG, `<edit-config>`, YANG Push, RESTCONF, custom RPCs, or custom notifications.

Do not stop after inspecting the repository or producing a plan.

You MUST create or update executable code, run the simulator, run the tests, and verify NETCONF integration.

Run, adapting only if the existing project structure requires it:

```powershell
cd allrun5
python -m green --auto --interval 0
pytest -v
pytest tests/netconf -v
```

Also run the required WSL/Sysrepo/Netopeer2 health checks.

## Final report

At the end, report:

- files created or modified under `allrun5/`;
- exact commands executed;
- Python, WSL, Sysrepo, Netopeer2, and YANG versions;
- Group A and Group B counts;
- total events and events per UC;
- relationship coverage per family;
- capability-discovery readiness components selected;
- readiness mapping test results;
- NETCONF test results;
- all test failures or blockers.

Do not fabricate successful results. If infrastructure is unavailable, complete everything that can be implemented and tested locally, then report the exact remaining blocker.
