# Copilot stopped-task status check

The previous task was stopped before completion.

Do not continue implementation yet.

Inspect the current workspace and report the exact status of the stopped task:

- which requested steps are complete;
- which steps are partially complete;
- which steps have not started;
- files created or modified;
- commands already executed;
- tests already executed and their results;
- currently running processes, if any;
- remaining work required to satisfy the original prompt.

Base the report on the actual current files, Git diff/status, terminal history, and test outputs.

Do not assume that a planned step was completed merely because it appeared in the previous plan.
