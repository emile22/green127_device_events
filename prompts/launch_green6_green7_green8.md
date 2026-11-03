# Launch green6, green7 and green8 sequentially

Run the following three prompts sequentially in the same task:

1. `/green6_controller_observe_all_UCs`
   using `green6_controller_observe_all_UCs.prompt.md`

2. `/green7_controller_process_all_UCs`
   using `green7_controller_process_all_UCs.prompt.md`

3. `/green8_yang_gap_analysis_all_UCs`
   using `green8_yang_gap_analysis_all_UCs.prompt.md`

These are implementation tasks, not analysis-only tasks.

## Execution rules

- Complete green6 first.
- green6 MUST create runnable controller code under `ctrlrun6/`.
- It must not stop after inspecting `allrun5/`, previous logs, Markdown files, or NETCONF outputs.
- Run the controller and its tests before continuing.

Expected green6 commands include:

```powershell
cd ctrlrun6
python -m green_controller --once
python -m green_controller --watch --interval 1
pytest -v
```

Then run green7.

- Use `allrun5/` and `ctrlrun6/` as read-only baselines.
- green7 MUST create runnable controller-processing code under `ctrlrun7/`.
- Implement filtering, transformation, aggregation, relationship traversal, provenance, network energy views, and deterministic recommendations.
- Do not perform YANG gap analysis.
- Do not assign GAP IDs.
- Do not modify YANG.
- Run the implementation and tests before continuing.

Expected green7 commands include:

```powershell
cd ctrlrun7
python -m green_controller --once
python -m green_controller --once --show-processing
pytest -v
```

Then run green8.

- Use `allrun5/`, `ctrlrun6/`, `ctrlrun7/`, and `ctrlrun7/docs/green8_input.json` as read-only evidence.
- green8 is the first step authorized to perform real YANG gap analysis.
- green8 MUST create runnable gap-analysis tooling under `gaprun8/`.
- Check each candidate against the actual current YANG schemas.
- Reject false candidates.
- Assign GAP IDs only to confirmed gaps.
- Add experimental YANG only for confirmed gaps.
- Never modify upstream IETF YANG files.
- Validate experimental modules and representative data.

Expected green8 commands include:

```powershell
cd gaprun8
python -m green_gap_tool analyze
python -m green_gap_tool validate
python -m green_gap_tool report
pytest -v
```

## General rules

- `allrun5/` remains read-only.
- `ctrlrun6/` becomes read-only once green6 is complete.
- `ctrlrun7/` becomes read-only once green7 is complete.
- Keep green6 output only under `ctrlrun6/`.
- Keep green7 output only under `ctrlrun7/`.
- Keep green8 output only under `gaprun8/`.
- Preserve the Windows Python / WSL Sysrepo-Netopeer2 architecture.
- Do not use containers.
- Do not add `<edit-config>`, RESTCONF, YANG Push, or NETCONF-driven device control unless explicitly required by a later prompt.
- If Sysrepo/Netopeer2 is temporarily unavailable, still implement executable code and run deterministic fixture-based tests; do not fall back to documentation-only output.
- If one step has a real blocking failure, stop before the dependent step and report the exact blocker.

## Final consolidated report

At the end provide one consolidated report with:

- code created in `ctrlrun6/`;
- code created in `ctrlrun7/`;
- code and experimental YANG created in `gaprun8/`;
- commands executed;
- test results;
- representation coverage from green7;
- confirmed and rejected YANG gaps from green8;
- exact experimental YANG additions;
- any remaining blockers.
