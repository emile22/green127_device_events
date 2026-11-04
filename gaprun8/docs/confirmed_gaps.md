# Confirmed YANG Gaps

## GAP-001 - UC 2.14 Energy Efficiency Under Power Shortage

- Events: U14-0, U14-1, U14-2, U14-3, U14-4, U14-5, U14-6, U14-7, U14-8, U14-9
- Requirement: Relate power-source and battery level to critical-service preservation and non-critical reduction.
- Category: STATE-GAP
- Scope: device operational state
- Confirmed because: A battery state-of-charge is a concrete UC 2.14 operational value demonstrated by U14-1 through U14-3. The active Energy Object schema has no typed state-of-charge leaf. RFC 8348 generic sensor-data is feature-gated (hardware-sensor is not enabled in the inspected Sysrepo module) and its `other` value plus display string does not identify state-of-charge as a machine-readable battery semantic.
- Local experimental path: `/ietf-power-and-energy:energy-objects/energy-object/example-green-power-energy-gaps:battery-state-of-charge/state-of-charge-percent`
- Config: `config false`; type/units: `decimal64 fraction-digits 2, range 0..100, units percent`
- Test: `test_soc_status_and_percent_validation`
