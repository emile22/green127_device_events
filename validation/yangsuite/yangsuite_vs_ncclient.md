# YANG Suite versus ncclient tests

Status: comparison not performed.

YANG Suite's dependency path includes `ncclient`; therefore the comparison is between its model-aware GUI/RPC workflow and the repository's existing ncclient test path, not between two independent NETCONF protocol implementations.

No paired request/reply was captured. Namespaces, filter scope, returned objects, values, identityrefs, relationship direction, and missing-leaf semantics remain uncompared. Do not change tests based on XML formatting alone. Compare semantically after the YANG Suite connection is available.