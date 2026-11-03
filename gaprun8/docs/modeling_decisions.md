# Modeling Decisions

Confirmed gaps: 1. Rejected green7 candidates: 13.

## Local Experimental Augmentation

- GAP-001: Add a local experimental battery-state-of-charge container with explicit available/unknown/unavailable status and a bounded percentage leaf.

## Possible Future IETF Work

The existing total-energy-consumed leaf declares units as Watt-hours while its description says mWh. YANG's units statement is machine-readable and is retained as authoritative here; an editorial clarification may be considered separately. This ambiguity was not assigned a GAP ID and was not changed locally.

All source schemas remain unchanged. The experimental module is local-only and is not an IETF standard.