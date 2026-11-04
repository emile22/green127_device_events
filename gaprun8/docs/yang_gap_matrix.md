# YANG Gap Matrix

## Use Case Names

| UC      | Use case name                                                                                               |
| ------- | ----------------------------------------------------------------------------------------------------------- |
| UC 2.1  | Incremental Application of the GREEN Framework                                                              |
| UC 2.2  | Selective reduction of energy consumption in network parts proportional to traffic levels                   |
| UC 2.3  | Reporting on Lifecycle Management                                                                           |
| UC 2.4  | Real-time Energy Metering of Virtualised or Cloud-native Network Functions                                  |
| UC 2.5  | Indirect Energy Monitoring and control                                                                      |
| UC 2.6  | Consideration of other domains for obtention of end-to-end metrics                                          |
| UC 2.7  | Dynamic adjustment of network element throughput according to traffic levels in wireless transport networks |
| UC 2.8  | Video streaming use case                                                                                    |
| UC 2.9  | WLAN Network Energy Saving                                                                                  |
| UC 2.10 | Fixed Network Energy Saving                                                                                 |
| UC 2.11 | Energy Efficiency Network Management                                                                        |
| UC 2.12 | ISAC-enabled Energy-Aware Smart City Traffic Management                                                     |
| UC 2.13 | Double Accounting Open issue                                                                                |
| UC 2.14 | Energy Efficiency Under Power Shortage                                                                      |
| UC 2.15 | Energy-Efficient Management of Distributed AI Training Workloads                                            |
| UC 2.16 | Network-level Cross Layer Energy Saving                                                                     |

## Summary

| UC      | Events                                                               | Gap?     | Scope                       | Coverage before | GAP ID  |
| ------- | -------------------------------------------------------------------- | -------- | --------------------------- | --------------- | ------- |
| UC 2.1  | U1-0, U1-1, U1-2, U1-3, U1-4, U1-5, U1-6, U1-7                       | No       | controller                  | absent          | -       |
| UC 2.2  | U2-0, U2-1, U2-2, U2-3, U2-4, U2-5, U2-6, U2-7, U2-8, U2-9           | No       | controller                  | absent          | -       |
| UC 2.5  | U5-0, U5-1, U5-2, U5-3, U5-4, U5-5, U5-6, U5-7                       | No       | controller                  | partial         | -       |
| UC 2.6  | U6-0, U6-1, U6-2, U6-3, U6-4, U6-5, U6-6, U6-7                       | No       | controller                  | partial         | -       |
| UC 2.7  | U7-0, U7-1, U7-2, U7-3, U7-4, U7-5, U7-6, U7-7                       | No       | controller                  | absent          | -       |
| UC 2.8  | U8-0, U8-1, U8-2, U8-3, U8-4, U8-5, U8-6, U8-7                       | No       | controller                  | absent          | -       |
| UC 2.9  | U9-0, U9-1, U9-2, U9-3, U9-4, U9-5, U9-6, U9-7, U9-8, U9-9           | No       | controller                  | partial         | -       |
| UC 2.10 | U10-0, U10-1, U10-2, U10-3, U10-4, U10-5, U10-6, U10-7               | No       | device                      | ambiguous       | -       |
| UC 2.11 | U11-0, U11-1, U11-2, U11-3, U11-4, U11-5, U11-6, U11-7               | No       | controller                  | partial         | -       |
| UC 2.12 | U12-0, U12-1, U12-2, U12-3, U12-4, U12-5, U12-6, U12-7, U12-8, U12-9 | No       | controller                  | absent          | -       |
| UC 2.13 | U13-0, U13-1, U13-2, U13-3, U13-4, U13-5, U13-6, U13-7               | No       | controller                  | partial         | -       |
| UC 2.14 | U14-0, U14-1, U14-2, U14-3, U14-4, U14-5, U14-6, U14-7, U14-8, U14-9 | Yes      | device operational state    | absent          | GAP-001 |
| UC 2.15 | U15-0, U15-1, U15-2, U15-3, U15-4, U15-5, U15-6, U15-7               | No       | controller                  | absent          | -       |
| UC 2.16 | U16-0, U16-1, U16-2, U16-3, U16-4, U16-5, U16-6, U16-7, U16-8, U16-9 | No       | controller                  | partial         | -       |
| UC 2.3  | -                                                                    | Deferred | controller/device reporting | underspecified  | -       |
| UC 2.4  | -                                                                    | Deferred | controller/device reporting | underspecified  | -       |

## Candidate Details

### UC 2.1 Incremental Application of the GREEN Framework

- Events: U1-0, U1-1, U1-2, U1-3, U1-4, U1-5, U1-6, U1-7
- Requirement: Retain provenance and uncertainty for the legacy baseline when comparing it with later measurements.
- Scope: controller
- Coverage before: absent
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
- Rationale: The baseline comparison and vendor source are controller-side provenance; existing data-source-accuracy identities cover measured, estimated, and static source quality, and no interoperable device baseline field is required by the event text.
- Test: -

### UC 2.2 Selective reduction of energy consumption in network parts proportional to traffic levels

- Events: U2-0, U2-1, U2-2, U2-3, U2-4, U2-5, U2-6, U2-7, U2-8, U2-9
- Requirement: Relate traffic condition and service continuity to component power-state transitions.
- Scope: controller
- Coverage before: absent
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
- Rationale: Traffic condition and service continuity are controller policy inputs; the device model already exposes current power and operational state, so no additional energy leaf is required.
- Test: -

### UC 2.5 Indirect Energy Monitoring and control

- Events: U5-0, U5-1, U5-2, U5-3, U5-4, U5-5, U5-6, U5-7
- Requirement: Distinguish a direct target measurement from an external meter correlated with an uninstrumented target.
- Scope: controller
- Coverage before: partial
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/measurement-local`
- Rationale: The model has measurement-local and directional metering/powering relationships. The target's unknown direct measurement remains correctly represented as unknown controller context.
- Test: -

### UC 2.6 Consideration of other domains for obtention of end-to-end metrics

- Events: U6-0, U6-1, U6-2, U6-3, U6-4, U6-5, U6-6, U6-7
- Requirement: Normalize domain inputs and retain the composition and boundary-guard provenance of an end-to-end value.
- Scope: controller
- Coverage before: partial
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship[type='aggregating']/peer`
- Rationale: Aggregating/aggregated-by and power/energy leaves represent the objects and readings; normalization, boundary guards, and lineage are processing provenance, not missing device state.
- Test: -

### UC 2.7 Dynamic adjustment of network element throughput according to traffic levels in wireless transport networks

- Events: U7-0, U7-1, U7-2, U7-3, U7-4, U7-5, U7-6, U7-7
- Requirement: Associate a radio throughput profile and traffic condition with observed link power.
- Scope: controller
- Coverage before: absent
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
- Rationale: Throughput profile and traffic condition are network-control context outside this energy-object operational model; the controller can retain them as metadata.
- Test: -

### UC 2.8 Video streaming use case

- Events: U8-0, U8-1, U8-2, U8-3, U8-4, U8-5, U8-6, U8-7
- Requirement: Relate delivery strategy and cache placement to observed energy values without asserting a standardized control protocol.
- Scope: controller
- Coverage before: absent
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
- Rationale: Delivery strategy and cache placement are application/controller context; the current energy objects already carry the observed power values.
- Test: -

### UC 2.9 WLAN Network Energy Saving

- Events: U9-0, U9-1, U9-2, U9-3, U9-4, U9-5, U9-6, U9-7, U9-8, U9-9
- Requirement: Relate AP power-state and PoE power changes to coverage and recovery-delay constraints.
- Scope: controller
- Coverage before: partial
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
- Rationale: The generic operational power-state leaf plus enabling, metering, and powering relationships represent the device state and topology; coverage and recovery-delay constraints are controller policy.
- Test: -

### UC 2.10 Fixed Network Energy Saving

- Events: U10-0, U10-1, U10-2, U10-3, U10-4, U10-5, U10-6, U10-7
- Requirement: Compare energy measurements over a defined interval and distinguish interval energy from cumulative counters.
- Scope: device
- Coverage before: ambiguous
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
- Rationale: The existing operational cumulative counter can be sampled and differenced by the controller; the controller records retrieval timestamps and can mark counter decreases/reset uncertainty incomplete. The machine-readable units statement declares Watt-hours; its conflicting prose is an editorial clarification candidate, not an unrepresentable node.
- Test: -

### UC 2.11 Energy Efficiency Network Management

- Events: U11-0, U11-1, U11-2, U11-3, U11-4, U11-5, U11-6, U11-7
- Requirement: Preserve telemetry history and distinguish optimized, legacy, and unknown capability classifications.
- Scope: controller
- Coverage before: partial
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/data-source-accuracy`
- Rationale: Existing data-source-accuracy identities cover measured/estimated/static/unavailable source quality; history and optimized/legacy classification are controller-derived.
- Test: -

### UC 2.12 ISAC-enabled Energy-Aware Smart City Traffic Management

- Events: U12-0, U12-1, U12-2, U12-3, U12-4, U12-5, U12-6, U12-7, U12-8, U12-9
- Requirement: Relate sensing mode and energy-aware routing to the requirement that critical sensing remains active.
- Scope: controller
- Coverage before: absent
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
- Rationale: Sensing modes, traffic routing, and critical-function policy are application/controller semantics; hardware state, power, and aggregation relationships are available for the energy view.
- Test: -

### UC 2.13 Double Accounting Open issue

- Events: U13-0, U13-1, U13-2, U13-3, U13-4, U13-5, U13-6, U13-7
- Requirement: Determine whether a measurement boundary is complete and whether a de-duplicated accounting result is authoritative.
- Scope: controller
- Coverage before: partial
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship[type='metering']/peer`
- Rationale: Existing directional metering relationships are sufficient to compute topology completeness and accounting status in the controller; no device-side completeness state is required.
- Test: -

### UC 2.14 Energy Efficiency Under Power Shortage

- Events: U14-0, U14-1, U14-2, U14-3, U14-4, U14-5, U14-6, U14-7, U14-8, U14-9
- Requirement: Relate power-source and battery level to critical-service preservation and non-critical reduction.
- Scope: device operational state
- Coverage before: absent
- Confirmed gap?: yes
- Category: STATE-GAP
- Proposed solution: Add a local experimental battery-state-of-charge container with explicit available/unknown/unavailable status and a bounded percentage leaf.
- Experimental module/path: /ietf-power-and-energy:energy-objects/energy-object/example-green-power-energy-gaps:battery-state-of-charge/state-of-charge-percent
- Config true/false: config false
- Units/type: decimal64 fraction-digits 2, range 0..100, units percent
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship[type='powering']/peer`
- Rationale: A battery state-of-charge is a concrete UC 2.14 operational value demonstrated by U14-1 through U14-3. The active Energy Object schema has no typed state-of-charge leaf. RFC 8348 generic sensor-data is feature-gated (hardware-sensor is not enabled in the inspected Sysrepo module) and its `other` value plus display string does not identify state-of-charge as a machine-readable battery semantic.
- Test: test_soc_status_and_percent_validation

### UC 2.15 Energy-Efficient Management of Distributed AI Training Workloads

- Events: U15-0, U15-1, U15-2, U15-3, U15-4, U15-5, U15-6, U15-7
- Requirement: Relate energy observations to scheduling window, active-node allocation, and data locality.
- Scope: controller
- Coverage before: absent
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
- Rationale: Scheduling windows, workload placement, and active-node policy are controller/application context; existing Energy Objects and power-state leaves expose the relevant device observations.
- Test: -

### UC 2.16 Network-level Cross Layer Energy Saving

- Events: U16-0, U16-1, U16-2, U16-3, U16-4, U16-5, U16-6, U16-7, U16-8, U16-9
- Requirement: Represent a cross-layer dependency check and preserve QoS during coordinated low-power transitions.
- Scope: controller
- Coverage before: partial
- Confirmed gap?: no
- Category: -
- Proposed solution: -
- Experimental module/path: -
- Config true/false: -
- Units/type: -
- Existing module/path:
  - `/ietf-hardware:hardware/component/name`
  - `/ietf-hardware:hardware/component/parent`
  - `/ietf-hardware:hardware/component/parent-rel-pos`
  - `/ietf-power-and-energy:energy-objects/energy-object/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/source-component-id`
  - `/ietf-power-and-energy:energy-objects/energy-object/power/instantaneous-power`
  - `/ietf-power-and-energy:energy-objects/energy-object/energy/total-energy-consumed`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/type`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship/peer/id`
  - `/ietf-power-and-energy:energy-objects/energy-object/relationship[type='enabling']/peer`
  - `/ietf-power-and-energy:energy-objects/energy-object/power-state/oper`
- Rationale: The enabling/enabled-by relationship models functional dependency; coordination progress and QoS policy remain controller-side decision context.
- Test: -

### UC 2.3 Reporting on Lifecycle Management (Group B)

- Decision: NOT A GAP candidate for this run.
- Modeling topics stated in the draft: lifecycle embedded-energy/carbon estimates for manufacturing, transport, recyclability, and end-of-life; location-based carbon factors and energy mix; backup-source identity and awareness of which backup is in use; vendor, datasheet, or database information ingestion
- Evidence: draft-ietf-green-use-cases.md, UC 2.3; allrun5/docs/deferred_group_b.md

### UC 2.4 Real-time Energy Metering of Virtualised or Cloud-native Network Functions (Group B)

- Decision: NOT A GAP candidate for this run.
- Modeling topics stated in the draft: real-time energy measurement for virtualized or cloud-native functions; metering across hardware and software layers; energy-aware management of dynamic workloads
- Evidence: draft-ietf-green-use-cases.md, UC 2.4; allrun5/docs/deferred_group_b.md

