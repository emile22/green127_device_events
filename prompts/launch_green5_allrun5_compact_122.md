# Launch green5 / allrun5

Run the implementation defined in:

`green5_netconf_all_UCs.prompt.md`

This is an implementation task, not an analysis-only task.

First inspect `minrun4/` and use it strictly as a read-only baseline.

Then create or update the complete implementation under:

`allrun5/`

Follow the prompt exactly.

## Important rules

- Do not modify `minrun4/`.
- Keep all implementation output under `allrun5/`.
- Implement all 14 Group A GREEN use cases.
- Keep UC 2.3 and UC 2.4 deferred.
- Preserve Windows Python + WSL Sysrepo/Netopeer2.
- Do not use containers.
- Keep NETCONF read-only.
- Preserve `ENTER/a/d/r/q`.
- Preserve raw NETCONF XML/JSON and detailed relationship views.
- Use the new compact line-oriented console layout by default.
- Do not use bordered tables, box-heavy panels, or a full-screen TUI for the normal event display.
- Prefer compact `HW`, `ENERGY`, `REL`, and `DIFF` lines.
- Double the event granularity exactly as required by the prompt.
- Ensure every UC meets its doubled minimum event count.
- Ensure total Group A event count is at least 122.
- Added events must be meaningful intermediate steps, not renamed duplicates.
- Preserve existing `minrun4` anchor events and values where required.
- Implement and test all four GREEN relationship families.
- Preserve stable RFC 8348 component names, UUIDs, Energy Object IDs, and `source-component-id` mappings.
- Implement capability-discovery readiness only.
- Do NOT implement RFC 9196 or `ietf-power-state-capabilities` in `allrun5`.
- Generate and test `allrun5/docs/capability_discovery_readiness.md`.
- Keep UC 2.11 capability classification as simulator/controller metadata only.
- Do not add `<edit-config>`, YANG Push, RESTCONF, custom RPCs, or custom notifications.

Do not stop after repository inspection, planning, or Markdown generation.

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

At the end report:

- files created or modified under `allrun5/`;
- exact commands executed;
- Python, WSL, Sysrepo, Netopeer2, and YANG versions;
- Group A and Group B counts;
- total Group A event count;
- confirmation that total Group A events >= 122;
- event count per UC;
- confirmation that each UC meets its doubled minimum;
- relationship coverage per family;
- capability-discovery readiness components selected;
- readiness mapping test results;
- NETCONF test results;
- all failures or blockers.

Do not fabricate successful results. If infrastructure is unavailable, complete everything that can still be implemented and tested locally, then report the exact remaining blocker.
