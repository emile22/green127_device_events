# Rejected Gap Candidates

Each item was checked against the actual repository YANG trees. Rejection means the candidate is represented adequately, is controller-scope, or lacks enough grounded semantic detail; it does not dismiss the use-case requirement.

## UC 2.1 Incremental Application of the GREEN Framework (U1-0, U1-1, U1-2, U1-3, U1-4, U1-5, U1-6, U1-7)
- Candidate: Retain provenance and uncertainty for the legacy baseline when comparing it with later measurements.
- Decision: NOT A GAP. The baseline comparison and vendor source are controller-side provenance; existing data-source-accuracy identities cover measured, estimated, and static source quality, and no interoperable device baseline field is required by the event text.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.2 Selective reduction of energy consumption in network parts proportional to traffic levels (U2-0, U2-1, U2-2, U2-3, U2-4, U2-5, U2-6, U2-7, U2-8, U2-9)
- Candidate: Relate traffic condition and service continuity to component power-state transitions.
- Decision: NOT A GAP. Traffic condition and service continuity are controller policy inputs; the device model already exposes current power and operational state, so no additional energy leaf is required.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.5 Indirect Energy Monitoring and control (U5-0, U5-1, U5-2, U5-3, U5-4, U5-5, U5-6, U5-7)
- Candidate: Distinguish a direct target measurement from an external meter correlated with an uninstrumented target.
- Decision: NOT A GAP. The model has measurement-local and directional metering/powering relationships. The target's unknown direct measurement remains correctly represented as unknown controller context.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.6 Consideration of other domains for obtention of end-to-end metrics (U6-0, U6-1, U6-2, U6-3, U6-4, U6-5, U6-6, U6-7)
- Candidate: Normalize domain inputs and retain the composition and boundary-guard provenance of an end-to-end value.
- Decision: NOT A GAP. Aggregating/aggregated-by and power/energy leaves represent the objects and readings; normalization, boundary guards, and lineage are processing provenance, not missing device state.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.7 Dynamic adjustment of network element throughput according to traffic levels in wireless transport networks (U7-0, U7-1, U7-2, U7-3, U7-4, U7-5, U7-6, U7-7)
- Candidate: Associate a radio throughput profile and traffic condition with observed link power.
- Decision: NOT A GAP. Throughput profile and traffic condition are network-control context outside this energy-object operational model; the controller can retain them as metadata.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.8 Video streaming use case (U8-0, U8-1, U8-2, U8-3, U8-4, U8-5, U8-6, U8-7)
- Candidate: Relate delivery strategy and cache placement to observed energy values without asserting a standardized control protocol.
- Decision: NOT A GAP. Delivery strategy and cache placement are application/controller context; the current energy objects already carry the observed power values.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.9 WLAN Network Energy Saving (U9-0, U9-1, U9-2, U9-3, U9-4, U9-5, U9-6, U9-7, U9-8, U9-9)
- Candidate: Relate AP power-state and PoE power changes to coverage and recovery-delay constraints.
- Decision: NOT A GAP. The generic operational power-state leaf plus enabling, metering, and powering relationships represent the device state and topology; coverage and recovery-delay constraints are controller policy.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.10 Fixed Network Energy Saving (U10-0, U10-1, U10-2, U10-3, U10-4, U10-5, U10-6, U10-7)
- Candidate: Compare energy measurements over a defined interval and distinguish interval energy from cumulative counters.
- Decision: NOT A GAP. The existing operational cumulative counter can be sampled and differenced by the controller; the controller records retrieval timestamps and can mark counter decreases/reset uncertainty incomplete. The machine-readable units statement declares Watt-hours; its conflicting prose is an editorial clarification candidate, not an unrepresentable node.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.11 Energy Efficiency Network Management (U11-0, U11-1, U11-2, U11-3, U11-4, U11-5, U11-6, U11-7)
- Candidate: Preserve telemetry history and distinguish optimized, legacy, and unknown capability classifications.
- Decision: NOT A GAP. Existing data-source-accuracy identities cover measured/estimated/static/unavailable source quality; history and optimized/legacy classification are controller-derived.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.12 ISAC-enabled Energy-Aware Smart City Traffic Management (U12-0, U12-1, U12-2, U12-3, U12-4, U12-5, U12-6, U12-7, U12-8, U12-9)
- Candidate: Relate sensing mode and energy-aware routing to the requirement that critical sensing remains active.
- Decision: NOT A GAP. Sensing modes, traffic routing, and critical-function policy are application/controller semantics; hardware state, power, and aggregation relationships are available for the energy view.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.13 Double Accounting Open issue (U13-0, U13-1, U13-2, U13-3, U13-4, U13-5, U13-6, U13-7)
- Candidate: Determine whether a measurement boundary is complete and whether a de-duplicated accounting result is authoritative.
- Decision: NOT A GAP. Existing directional metering relationships are sufficient to compute topology completeness and accounting status in the controller; no device-side completeness state is required.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.15 Energy-Efficient Management of Distributed AI Training Workloads (U15-0, U15-1, U15-2, U15-3, U15-4, U15-5, U15-6, U15-7)
- Candidate: Relate energy observations to scheduling window, active-node allocation, and data locality.
- Decision: NOT A GAP. Scheduling windows, workload placement, and active-node policy are controller/application context; existing Energy Objects and power-state leaves expose the relevant device observations.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.16 Network-level Cross Layer Energy Saving (U16-0, U16-1, U16-2, U16-3, U16-4, U16-5, U16-6, U16-7, U16-8, U16-9)
- Candidate: Represent a cross-layer dependency check and preserve QoS during coordinated low-power transitions.
- Decision: NOT A GAP. The enabling/enabled-by relationship models functional dependency; coordination progress and QoS policy remain controller-side decision context.
- Schema evidence: ietf-hardware:name present in pyang tree; ietf-hardware:parent present in pyang tree; ietf-hardware:parent-rel-pos present in pyang tree; ietf-power-and-energy:id present in pyang tree

## UC 2.3 Reporting on Lifecycle Management (Group B)
- Decision: NOT A GAP candidate for this run. The draft describes lifecycle reporting inputs and external metadata but gives no concrete event sequence, collection timing, or interoperable device data contract. No lifecycle transitions or external-data behavior are invented.
- Modeling topics stated in the draft: lifecycle embedded-energy/carbon estimates for manufacturing, transport, recyclability, and end-of-life; location-based carbon factors and energy mix; backup-source identity and awareness of which backup is in use; vendor, datasheet, or database information ingestion
- Evidence: draft-ietf-green-use-cases.md, UC 2.3; allrun5/docs/deferred_group_b.md

## UC 2.4 Real-time Energy Metering of Virtualised or Cloud-native Network Functions (Group B)
- Decision: NOT A GAP candidate for this run. The draft states a high-level metering need but leaves GREEN requirements as TODO; it does not define virtual entity identity, host correlation, shared-energy attribution, migration behavior, or event timing.
- Modeling topics stated in the draft: real-time energy measurement for virtualized or cloud-native functions; metering across hardware and software layers; energy-aware management of dynamic workloads
- Evidence: draft-ietf-green-use-cases.md, UC 2.4; allrun5/docs/deferred_group_b.md
