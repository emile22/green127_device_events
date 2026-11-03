# YANG Suite NETCONF stack

## Finding

The inspected YANG Suite dependency metadata/source identified `ncclient` in the NETCONF path, and the installed environment reported `ncclient` 0.7.1. The NETCONF plugin uses `ncclient_send` for its client operations. Classify YANG Suite as:

> B. Independent GUI/schema/RPC workflow using ncclient underneath.

It is not an independent NETCONF protocol implementation. YANG Suite provides the UI, model-aware workflow, and RPC construction around the client library.

## Installation caveat

The first install's `pip check` passed. A later WSL I/O failure left the CLI entry point and Django files truncated. On 2026-11-02 the pinned packages and dependency graph were reinstalled; `pip check` passed, CLI help ran, and the Windows launcher started the web service with an HTTP 200 response. See [version-report.txt](version-report.txt).

No NETCONF session was established, so this finding classifies the installed dependency path only; it does not claim that the live plugin connected to Netopeer2.