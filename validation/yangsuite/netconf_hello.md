# NETCONF hello

Status: not captured.

YANG Suite did not reach a verified running state, and no NETCONF session was established. Therefore no server `<hello>`, NETCONF base capabilities, YANG Library capability, or other Netopeer2 capability is reported here.

Do not infer power-state capability discovery from NETCONF `<hello>`:

- NETCONF `<hello>` advertises NETCONF/server protocol functionality.
- RFC 9196 / power-state capability discovery is modeled operational data.

After filesystem recovery, connect to the verified Netopeer2 listener using a local YANG Suite device profile and record sanitized capability URIs here.