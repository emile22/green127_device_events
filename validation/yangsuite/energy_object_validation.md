# Energy Object validation

Status: not performed; no live data or XML was captured.

No Energy Objects, hardware components, `source-component-id` mappings, power/state leaves, or relationships were read through YANG Suite. All six topology families remain unvalidated:

- T1 CORE: Fixed Network
- T2 AIR: WLAN / PoE
- T3 POWER: Power Infrastructure
- T4 BACKHAUL: Wireless Transport
- T5 EDGE: Edge / Compute
- T6 CITY: ISAC / Smart City

When testing resumes, record each Energy Object ID, source component ID, matching hardware component name and UUID separately, power/state leaf presence and value, and relationship peer/direction. Preserve the typed YANG XML. In particular, verify that unavailable numeric values are omitted rather than encoded as zero or as `UNKNOWN`/`N/A` strings; zero must remain an actual value where modeled.

The four relationship families to inspect are METERING/METERED-BY, AGGREGATING/AGGREGATED-BY, POWERING/POWERED-BY, and ENABLING/ENABLED-BY. Direction, inverse semantics, self-reference, and duplicates remain unchecked.