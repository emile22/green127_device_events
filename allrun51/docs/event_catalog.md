# Group A Event Catalog

This catalog is generated from `src/green/catalog.py`: 14 use cases, 122 deterministic events.

Event IDs and descriptions are simulator-specific and are not standardized IETF event names.

## UC 2.1 - Incremental Application of the GREEN Framework

| UC     | Event ID | Event name                  | Relationship families |
| ------ | -------- | --------------------------- | --------------------- |
| UC 2.1 | U1-0     | LEGACY_BASELINE             | none                  |
| UC 2.1 | U1-1     | COMPONENT_GREEN_ENABLED     | none                  |
| UC 2.1 | U1-2     | DEVICE_GREEN_ENABLED        | none                  |
| UC 2.1 | U1-3     | NETWORK_MIXED_DEPLOYMENT    | none                  |
| UC 2.1 | U1-4     | LEGACY_REFERENCE_REVIEWED   | none                  |
| UC 2.1 | U1-5     | COMPONENT_MAPPING_VERIFIED  | none                  |
| UC 2.1 | U1-6     | PARTIAL_COVERAGE_RECORDED   | none                  |
| UC 2.1 | U1-7     | MIXED_DEPLOYMENT_RECONCILED | none                  |

### U1-0 - LEGACY_BASELINE

- Description: Legacy equipment begins with vendor reference data but no direct GREEN telemetry.
- Main state/data: metadata-only simulator step
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id
- Simulator-only metadata: baseline-power-w=500; baseline-source=vendor-datasheet; green-telemetry=unknown; classification=baseline-only; baseline-energy-object-id=eo-router-a

### U1-1 - COMPONENT_GREEN_ENABLED

- Description: One component gains GREEN telemetry while the rest of the router remains unmeasured.
- Main state/data: eo-router-a-linecard-1=active; eo-router-a-linecard-1=120 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: linecard-1-status=measured; linecard-2-status=legacy-unmeasured

### U1-2 - DEVICE_GREEN_ENABLED

- Description: Device-wide measurements are compared with the original legacy baseline.
- Main state/data: eo-router-a=active; eo-router-a=420 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: baseline-power-w=500; observed-power-w=420; power-delta-w=-80; power-reduction-percent=16; baseline-event-name=DEVICE_CONTROLLER_GREEN

### U1-3 - NETWORK_MIXED_DEPLOYMENT

- Description: The network combines partially migrated and fully GREEN-enabled devices.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-a=420 W; eo-router-b=380 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: router-A-data-classification=measured; router-B-data-classification=measured; network-stage=NETWORK_LEVEL_GREEN

### U1-4 - LEGACY_REFERENCE_REVIEWED

- Description: The legacy power estimate remains separate from unavailable direct telemetry.
- Main state/data: metadata-only simulator step
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper
- Simulator-only metadata: baseline-source=vendor-datasheet; green-telemetry=unknown

### U1-5 - COMPONENT_MAPPING_VERIFIED

- Description: The observed line-card reading maps to one stable hardware component.
- Main state/data: eo-router-a-linecard-1=active; eo-router-a-linecard-1=120 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: mapping-status=verified; unmeasured-component=linecard-2

### U1-6 - PARTIAL_COVERAGE_RECORDED

- Description: The second line card remains unmeasured while device power is available.
- Main state/data: eo-router-a=active; eo-router-a=420 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: linecard-1-status=measured; linecard-2-status=unknown

### U1-7 - MIXED_DEPLOYMENT_RECONCILED

- Description: Network reporting distinguishes measured devices from the legacy baseline.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-a=420 W; eo-router-b=380 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: router-A-class=measured; router-B-class=measured; legacy-reference-retained=true

## UC 2.2 - Selective reduction of energy consumption proportional to traffic

| UC     | Event ID | Event name                    | Relationship families |
| ------ | -------- | ----------------------------- | --------------------- |
| UC 2.2 | U2-0     | TRAFFIC_PEAK                  | none                  |
| UC 2.2 | U2-1     | TRAFFIC_VALLEY                | none                  |
| UC 2.2 | U2-2     | TRAFFIC_RELOCATED             | none                  |
| UC 2.2 | U2-3     | COMPONENTS_SLEEPING           | none                  |
| UC 2.2 | U2-4     | TRAFFIC_RECOVERY              | none                  |
| UC 2.2 | U2-5     | TRAFFIC_THRESHOLD_ESTABLISHED | none                  |
| UC 2.2 | U2-6     | CAPACITY_PATH_SELECTED        | none                  |
| UC 2.2 | U2-7     | SLEEP_ELIGIBILITY_RECORDED    | none                  |
| UC 2.2 | U2-8     | RECOVERY_DEMAND_DETECTED      | none                  |
| UC 2.2 | U2-9     | SERVICE_CAPACITY_RESTORED     | none                  |

### U2-0 - TRAFFIC_PEAK

- Description: Peak traffic keeps the service path active at its planned capacity.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-a=500 W; eo-router-b=480 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=peak; service-continuity=maintained

### U2-1 - TRAFFIC_VALLEY

- Description: A traffic valley permits lower component power while service remains available.
- Main state/data: eo-router-a=low-power; eo-router-b=active; eo-router-a=340 W; eo-router-b=330 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=valley; optimization=component low-power

### U2-2 - TRAFFIC_RELOCATED

- Description: Traffic is concentrated on one path so lightly loaded components can save energy.
- Main state/data: eo-router-a=low-power; eo-router-b=active; eo-router-a=250 W; eo-router-b=390 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-action=relocated-to-router-B; service-continuity=maintained

### U2-3 - COMPONENTS_SLEEPING

- Description: Unused line-card capacity enters sleep after traffic relocation.
- Main state/data: eo-router-a-linecard-1=low-power; eo-router-a=220 W; eo-router-b=390 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: sleeping-component=linecard-1; service-continuity=maintained

### U2-4 - TRAFFIC_RECOVERY

- Description: Returning demand wakes capacity before traffic exceeds the service path.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-a-linecard-1=active; eo-router-a=460 W; eo-router-b=470 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=recovery; service-continuity=maintained

### U2-5 - TRAFFIC_THRESHOLD_ESTABLISHED

- Description: Observed demand is compared with the service capacity threshold.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-a=490 W; eo-router-b=470 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=high; capacity-threshold=simulated

### U2-6 - CAPACITY_PATH_SELECTED

- Description: Traffic is concentrated on the path with sufficient service headroom.
- Main state/data: eo-router-a=low-power; eo-router-b=active; eo-router-a=390 W; eo-router-b=450 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-action=concentrated-on-router-B; service-continuity=maintained

### U2-7 - SLEEP_ELIGIBILITY_RECORDED

- Description: An unused line card is identified for sleep after traffic relocation.
- Main state/data: eo-router-a-linecard-1=low-power; eo-router-a=280 W; eo-router-b=420 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: sleep-candidate=linecard-1; traffic-action=relocated

### U2-8 - RECOVERY_DEMAND_DETECTED

- Description: Returning demand triggers a wake decision before capacity is exceeded.
- Main state/data: eo-router-a-linecard-1=low-power; eo-router-a=360 W; eo-router-b=440 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=recovering; wake-decision=required

### U2-9 - SERVICE_CAPACITY_RESTORED

- Description: The line card returns to service while the traffic path remains available.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-a-linecard-1=active; eo-router-a=470 W; eo-router-b=475 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=recovered; service-continuity=maintained

## UC 2.5 - Indirect Energy Monitoring and control

| UC     | Event ID | Event name                           | Relationship families                        |
| ------ | -------- | ------------------------------------ | -------------------------------------------- |
| UC 2.5 | U5-0     | TARGET_UNINSTRUMENTED                | metering / metered-by, powering / powered-by |
| UC 2.5 | U5-1     | EXTERNAL_METER_DISCOVERED            | metering / metered-by, powering / powered-by |
| UC 2.5 | U5-2     | INDIRECT_MEASUREMENT_ACTIVE          | metering / metered-by, powering / powered-by |
| UC 2.5 | U5-3     | UPSTREAM_POWER_CONTROL_AVAILABLE     | metering / metered-by, powering / powered-by |
| UC 2.5 | U5-4     | PDU_OUTLET_BASELINE_CAPTURED         | metering / metered-by, powering / powered-by |
| UC 2.5 | U5-5     | METER_TO_TARGET_CORRELATION_VERIFIED | metering / metered-by, powering / powered-by |
| UC 2.5 | U5-6     | INDIRECT_LOAD_CHANGE_OBSERVED        | metering / metered-by, powering / powered-by |
| UC 2.5 | U5-7     | MEASUREMENT_PATH_REVALIDATED         | metering / metered-by, powering / powered-by |

### U5-0 - TARGET_UNINSTRUMENTED

- Description: The legacy target has no direct sensor, so its consumption remains unknown.
- Main state/data: eo-pdu-outlet-1=720 W
- Relationship families: metering / metered-by, powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: target-direct-measurement=unknown; management-source=PDU outlet

### U5-1 - EXTERNAL_METER_DISCOVERED

- Description: An instrumented PDU outlet is identified as the target's indirect measurement source.
- Main state/data: eo-pdu-outlet-1=720 W
- Relationship families: metering / metered-by, powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: target-direct-measurement=unknown; external-meter=pdu-outlet-1

### U5-2 - INDIRECT_MEASUREMENT_ACTIVE

- Description: The PDU outlet reports power for the target without fabricating a target sensor value.
- Main state/data: eo-pdu-outlet-1=680 W
- Relationship families: metering / metered-by, powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: measurement-method=indirect; target-direct-measurement=unknown

### U5-3 - UPSTREAM_POWER_CONTROL_AVAILABLE

- Description: The upstream outlet exposes a simulated power-control capability for the legacy target.
- Main state/data: eo-pdu-outlet-1=680 W
- Relationship families: metering / metered-by, powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: control-path=pdu-outlet-1; target-direct-measurement=unknown

### U5-4 - PDU_OUTLET_BASELINE_CAPTURED

- Description: The external outlet provides a baseline while direct target measurement remains unknown.
- Main state/data: eo-pdu-outlet-1=720 W
- Relationship families: metering / metered-by, powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: target-direct-measurement=unknown; measurement-method=indirect

### U5-5 - METER_TO_TARGET_CORRELATION_VERIFIED

- Description: The outlet relationship identifies the source of the target's indirect reading.
- Main state/data: eo-pdu-outlet-1=710 W
- Relationship families: metering / metered-by, powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: target-direct-measurement=unknown; correlation=verified

### U5-6 - INDIRECT_LOAD_CHANGE_OBSERVED

- Description: A changed outlet reading is recorded without assigning it to a target sensor.
- Main state/data: eo-pdu-outlet-1=660 W
- Relationship families: metering / metered-by, powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: target-direct-measurement=unknown; measurement-method=indirect

### U5-7 - MEASUREMENT_PATH_REVALIDATED

- Description: The external meter remains the only measured source for the legacy target.
- Main state/data: eo-pdu-outlet-1=650 W
- Relationship families: metering / metered-by, powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: target-direct-measurement=unknown; source-status=verified

## UC 2.6 - Consideration of other domains for obtention of end-to-end metrics

| UC     | Event ID | Event name                    | Relationship families       |
| ------ | -------- | ----------------------------- | --------------------------- |
| UC 2.6 | U6-0     | DOMAIN_METRICS_AVAILABLE      | aggregating / aggregated-by |
| UC 2.6 | U6-1     | METRICS_MAPPED                | aggregating / aggregated-by |
| UC 2.6 | U6-2     | DOUBLE_COUNTING_GUARD_APPLIED | aggregating / aggregated-by |
| UC 2.6 | U6-3     | END_TO_END_METRIC_COMPOSED    | aggregating / aggregated-by |
| UC 2.6 | U6-4     | DOMAIN_INPUTS_VALIDATED       | aggregating / aggregated-by |
| UC 2.6 | U6-5     | UNIT_MAPPING_CONFIRMED        | aggregating / aggregated-by |
| UC 2.6 | U6-6     | SHARED_BOUNDARY_REVIEWED      | aggregating / aggregated-by |
| UC 2.6 | U6-7     | COMPOSED_VIEW_RECONCILED      | aggregating / aggregated-by |

### U6-0 - DOMAIN_METRICS_AVAILABLE

- Description: Access and transport domains report metrics for one end-to-end service.
- Main state/data: eo-domain-energy-aggregator=1800 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: access-domain-energy-wh=420; transport-domain-energy-wh=680; core-domain-energy-wh=700

### U6-1 - METRICS_MAPPED

- Description: Domain metrics are mapped to a common energy unit before composition.
- Main state/data: eo-domain-energy-aggregator=1750 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: mapping-status=normalized-to-Wh; source-domains=access,transport,core

### U6-2 - DOUBLE_COUNTING_GUARD_APPLIED

- Description: Domain boundaries are checked so shared energy is not counted twice.
- Main state/data: eo-domain-energy-aggregator=1710 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: accounting-guard=domain-boundary; shared-energy-added-once=true

### U6-3 - END_TO_END_METRIC_COMPOSED

- Description: Normalized domain contributions form one controller-side end-to-end view.
- Main state/data: eo-domain-energy-aggregator=1710 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: composition-status=complete; end-to-end-energy-wh=1800; data-classification=simulator-composition

### U6-4 - DOMAIN_INPUTS_VALIDATED

- Description: Access, transport, and core inputs are checked before end-to-end composition.
- Main state/data: eo-domain-energy-aggregator=1700 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: source-domains=access,transport,core; input-validation=complete

### U6-5 - UNIT_MAPPING_CONFIRMED

- Description: Domain energy values share a common unit before they are combined.
- Main state/data: eo-domain-energy-aggregator=1690 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: mapping-status=normalized-to-Wh; unit-check=passed

### U6-6 - SHARED_BOUNDARY_REVIEWED

- Description: The accounting boundary is reviewed before shared domain energy is included.
- Main state/data: eo-domain-energy-aggregator=1680 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: accounting-guard=domain-boundary; shared-energy=reviewed

### U6-7 - COMPOSED_VIEW_RECONCILED

- Description: The composed result retains its source domains and controller-side provenance.
- Main state/data: eo-domain-energy-aggregator=1680 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: composition-status=reconciled; data-classification=simulator-composition

## UC 2.7 - Dynamic adjustment of network element throughput in wireless transport

| UC     | Event ID | Event name               | Relationship families |
| ------ | -------- | ------------------------ | --------------------- |
| UC 2.7 | U7-0     | PEAK_TRAFFIC_LINK_POWER  | none                  |
| UC 2.7 | U7-1     | NORMAL_TRAFFIC_DETECTED  | none                  |
| UC 2.7 | U7-2     | RADIO_LINK_POWER_REDUCED | none                  |
| UC 2.7 | U7-3     | PEAK_TRAFFIC_RESTORED    | none                  |
| UC 2.7 | U7-4     | LINK_LOAD_RECHECKED      | none                  |
| UC 2.7 | U7-5     | REDUCED_PROFILE_SELECTED | none                  |
| UC 2.7 | U7-6     | LINK_HEADROOM_CONFIRMED  | none                  |
| UC 2.7 | U7-7     | PEAK_PROFILE_RESTORED    | none                  |

### U7-0 - PEAK_TRAFFIC_LINK_POWER

- Description: Peak traffic configures the wireless transport link for its planned capacity.
- Main state/data: eo-wireless-link-1=active; eo-wireless-link-1=1600 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=peak; throughput-profile=maximum

### U7-1 - NORMAL_TRAFFIC_DETECTED

- Description: Observed normal traffic leaves headroom to reduce wireless link power.
- Main state/data: eo-wireless-link-1=active; eo-wireless-link-1=1350 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=normal; measurement-source=link telemetry

### U7-2 - RADIO_LINK_POWER_REDUCED

- Description: The radio link adopts a lower power profile proportional to observed traffic.
- Main state/data: eo-wireless-link-1=low-power; eo-wireless-link-1=920 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: power-profile=reduced; service-continuity=maintained

### U7-3 - PEAK_TRAFFIC_RESTORED

- Description: A traffic peak restores the link's high-capacity power profile.
- Main state/data: eo-wireless-link-1=active; eo-wireless-link-1=1600 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=peak; throughput-profile=maximum

### U7-4 - LINK_LOAD_RECHECKED

- Description: A fresh link reading confirms demand remains below the peak profile.
- Main state/data: eo-wireless-link-1=active; eo-wireless-link-1=1280 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=normal; measurement-source=link telemetry

### U7-5 - REDUCED_PROFILE_SELECTED

- Description: The link uses a lower power profile while preserving the service path.
- Main state/data: eo-wireless-link-1=low-power; eo-wireless-link-1=1080 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: power-profile=reduced; service-continuity=maintained

### U7-6 - LINK_HEADROOM_CONFIRMED

- Description: Observed traffic leaves enough headroom to maintain the reduced profile.
- Main state/data: eo-wireless-link-1=low-power; eo-wireless-link-1=980 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=low; throughput-profile=reduced

### U7-7 - PEAK_PROFILE_RESTORED

- Description: Rising traffic restores the link's high-capacity operational profile.
- Main state/data: eo-wireless-link-1=active; eo-wireless-link-1=1550 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: traffic-condition=peak; throughput-profile=maximum

## UC 2.8 - Video streaming use case

| UC     | Event ID | Event name                         | Relationship families |
| ------ | -------- | ---------------------------------- | --------------------- |
| UC 2.8 | U8-0     | HIGH_UNICAST_DEMAND                | none                  |
| UC 2.8 | U8-1     | MULTICAST_DELIVERY_ENABLED         | none                  |
| UC 2.8 | U8-2     | CACHE_PLACED_NEAR_USERS            | none                  |
| UC 2.8 | U8-3     | REDUNDANT_BACKBONE_TRAFFIC_REDUCED | none                  |
| UC 2.8 | U8-4     | CONTENT_DEMAND_PROFILED            | none                  |
| UC 2.8 | U8-5     | CACHE_HIT_RATE_IMPROVED            | none                  |
| UC 2.8 | U8-6     | BACKBONE_TRANSFER_REDUCED          | none                  |
| UC 2.8 | U8-7     | DELIVERY_MIX_STABILIZED            | none                  |

### U8-0 - HIGH_UNICAST_DEMAND

- Description: Separate unicast streams increase repeated traffic across the backbone.
- Main state/data: eo-video-origin-1=900 W; eo-router-a=1100 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power
- Simulator-only metadata: delivery-strategy=unicast; video-demand=high

### U8-1 - MULTICAST_DELIVERY_ENABLED

- Description: A simulated multicast delivery choice reduces duplicate video flows on shared paths.
- Main state/data: eo-video-origin-1=700 W; eo-router-a=850 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power
- Simulator-only metadata: delivery-strategy=multicast-demonstration; standardized-control-protocol=not-claimed

### U8-2 - CACHE_PLACED_NEAR_USERS

- Description: A nearby cache serves popular content and shortens repeated backbone transfers.
- Main state/data: eo-video-cache-1=420 W; eo-router-a=620 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power
- Simulator-only metadata: cache-placement=near-users; content-transfer=localized

### U8-3 - REDUNDANT_BACKBONE_TRAFFIC_REDUCED

- Description: Local delivery reduces redundant backbone traffic while preserving the video service.
- Main state/data: eo-video-cache-1=450 W; eo-router-a=540 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power
- Simulator-only metadata: backbone-traffic=reduced; service-continuity=maintained

### U8-4 - CONTENT_DEMAND_PROFILED

- Description: Popular content is identified before selecting a local delivery strategy.
- Main state/data: eo-video-origin-1=680 W; eo-router-a=790 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power
- Simulator-only metadata: video-demand=popular-content; delivery-strategy=unicast

### U8-5 - CACHE_HIT_RATE_IMPROVED

- Description: A nearby cache serves more requests and reduces repeated origin transfers.
- Main state/data: eo-video-cache-1=460 W; eo-router-a=760 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power
- Simulator-only metadata: cache-placement=near-users; cache-hit-rate=increased

### U8-6 - BACKBONE_TRANSFER_REDUCED

- Description: Localized delivery lowers backbone work while preserving the streaming service.
- Main state/data: eo-video-cache-1=470 W; eo-router-a=590 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power
- Simulator-only metadata: content-transfer=localized; backbone-traffic=reduced

### U8-7 - DELIVERY_MIX_STABILIZED

- Description: The simulated delivery mix remains stable after cache placement and traffic reduction.
- Main state/data: eo-video-origin-1=520 W; eo-video-cache-1=470 W; eo-router-a=590 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power
- Simulator-only metadata: delivery-strategy=mixed-demonstration; standardized-control-protocol=not-claimed

## UC 2.9 - WLAN Network Energy Saving

| UC     | Event ID | Event name                    | Relationship families                                               |
| ------ | -------- | ----------------------------- | ------------------------------------------------------------------- |
| UC 2.9 | U9-0     | AP_ACTIVE                     | metering / metered-by, powering / powered-by, enabling / enabled-by |
| UC 2.9 | U9-1     | AP_LOW_POWER                  | metering / metered-by, powering / powered-by, enabling / enabled-by |
| UC 2.9 | U9-2     | AP_HIBERNATING                | metering / metered-by, powering / powered-by, enabling / enabled-by |
| UC 2.9 | U9-3     | POE_POWER_OFF                 | metering / metered-by, powering / powered-by, enabling / enabled-by |
| UC 2.9 | U9-4     | AP_REACTIVATED                | metering / metered-by, powering / powered-by, enabling / enabled-by |
| UC 2.9 | U9-5     | RADIO_LOAD_REVIEWED           | metering / metered-by, powering / powered-by, enabling / enabled-by |
| UC 2.9 | U9-6     | BAND_SLEEP_CONFIRMED          | metering / metered-by, powering / powered-by, enabling / enabled-by |
| UC 2.9 | U9-7     | HIBERNATION_WAKE_PATH_CHECKED | metering / metered-by, powering / powered-by, enabling / enabled-by |
| UC 2.9 | U9-8     | COVERAGE_RECOVERY_STARTED     | metering / metered-by, powering / powered-by, enabling / enabled-by |
| UC 2.9 | U9-9     | FULL_COVERAGE_CONFIRMED       | metering / metered-by, powering / powered-by, enabling / enabled-by |

### U9-0 - AP_ACTIVE

- Description: The PoE-powered access point serves both radio bands at full operation.
- Main state/data: eo-ap-1=active; eo-ap-radio-24=active; eo-ap-radio-5=active; eo-ap-1=18000 W; eo-poe-port-ap1=20000 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=active; coverage=normal

### U9-1 - AP_LOW_POWER

- Description: The access point disables a radio band while retaining limited connectivity.
- Main state/data: eo-ap-1=low-power; eo-ap-radio-24=active; eo-ap-radio-5=off; eo-ap-1=11500 W; eo-poe-port-ap1=13000 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=low-power; available-band=2.4GHz

### U9-2 - AP_HIBERNATING

- Description: The access point hibernates nonessential components while preserving its wake path.
- Main state/data: eo-ap-1=hibernating; eo-ap-1=3200 W; eo-poe-port-ap1=4800 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=hibernating; standard-yang-power-state=not-defined

### U9-3 - POE_POWER_OFF

- Description: The PoE port removes power from the access point, with recovery delay expected.
- Main state/data: eo-ap-1=off; eo-poe-port-ap1=off; eo-poe-port-ap1=0 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=poe-power-off; recovery-delay=minutes

### U9-4 - AP_REACTIVATED

- Description: The PoE port restores power and the access point resumes normal coverage.
- Main state/data: eo-ap-1=active; eo-ap-radio-24=active; eo-ap-radio-5=active; eo-poe-port-ap1=active; eo-ap-1=18000 W; eo-poe-port-ap1=20000 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=active; coverage=restored

### U9-5 - RADIO_LOAD_REVIEWED

- Description: Radio demand is reviewed before selecting a lower-power WLAN mode.
- Main state/data: eo-ap-1=active; eo-ap-1=16000 W; eo-poe-port-ap1=18000 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=active; radio-load=reviewed

### U9-6 - BAND_SLEEP_CONFIRMED

- Description: The unused five-gigahertz band sleeps while the two-point-four-gigahertz band remains active.
- Main state/data: eo-ap-1=low-power; eo-ap-radio-24=active; eo-ap-radio-5=off; eo-ap-1=10000 W; eo-poe-port-ap1=12000 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=low-power; available-band=2.4GHz

### U9-7 - HIBERNATION_WAKE_PATH_CHECKED

- Description: The access point hibernates after its wake path and PoE supply are checked.
- Main state/data: eo-ap-1=hibernating; eo-ap-1=2800 W; eo-poe-port-ap1=4300 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=hibernating; wake-path=available

### U9-8 - COVERAGE_RECOVERY_STARTED

- Description: The PoE supply restores the access point before full radio coverage returns.
- Main state/data: eo-ap-1=low-power; eo-poe-port-ap1=active; eo-ap-1=9000 W; eo-poe-port-ap1=11000 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=recovering; coverage=restoring

### U9-9 - FULL_COVERAGE_CONFIRMED

- Description: Both radio bands resume service after the recovery state is verified.
- Main state/data: eo-ap-1=active; eo-ap-radio-24=active; eo-ap-radio-5=active; eo-poe-port-ap1=active; eo-ap-1=18000 W; eo-poe-port-ap1=20000 W
- Relationship families: metering / metered-by, powering / powered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: wlan-mode=active; coverage=restored

## UC 2.10 - Fixed Network Energy Saving

| UC      | Event ID | Event name                  | Relationship families                        |
| ------- | -------- | --------------------------- | -------------------------------------------- |
| UC 2.10 | U10-0    | TRAFFIC_HIGH                | metering / metered-by, enabling / enabled-by |
| UC 2.10 | U10-1    | TRAFFIC_LOW                 | metering / metered-by, enabling / enabled-by |
| UC 2.10 | U10-2    | COMPONENT_SLEEP             | metering / metered-by, enabling / enabled-by |
| UC 2.10 | U10-3    | TRAFFIC_BURST               | metering / metered-by, enabling / enabled-by |
| UC 2.10 | U10-4    | METERED_INTERVAL_RECORDED   | metering / metered-by, enabling / enabled-by |
| UC 2.10 | U10-5    | SLEEP_STATE_VERIFIED        | metering / metered-by, enabling / enabled-by |
| UC 2.10 | U10-6    | WAKE_RESPONSE_MEASURED      | metering / metered-by, enabling / enabled-by |
| UC 2.10 | U10-7    | RECOVERY_INTERVAL_CONFIRMED | metering / metered-by, enabling / enabled-by |

### U10-0 - TRAFFIC_HIGH

- Description: High traffic keeps both components active and produces the highest normal energy demand.
- Main state/data: eo-server-a=active; eo-server-b=active; eo-router-a=500 W; eo-router-b=480 W; eo-upstream-meter=300 Wh interval, 300 Wh cumulative; eo-server-a=120 Wh interval, 120 Wh cumulative; eo-server-b=180 Wh interval, 180 Wh cumulative
- Relationship families: metering / metered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, energy/total-energy-consumed, relationship/type,peer/id
- Simulator-only metadata: none

### U10-1 - TRAFFIC_LOW

- Description: Lower traffic reduces component activity and decreases measured energy consumption.
- Main state/data: eo-server-a=active; eo-server-b=active; eo-router-a=340 W; eo-router-b=330 W; eo-upstream-meter=150 Wh interval, 450 Wh cumulative; eo-server-a=60 Wh interval, 180 Wh cumulative; eo-server-b=90 Wh interval, 270 Wh cumulative
- Relationship families: metering / metered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, energy/total-energy-consumed, relationship/type,peer/id
- Simulator-only metadata: none

### U10-2 - COMPONENT_SLEEP

- Description: Low traffic lets server-B enter low-power mode and reduce consumption.
- Main state/data: eo-server-a=active; eo-server-b=low-power; eo-router-a=220 W; eo-router-b=390 W; eo-upstream-meter=80 Wh interval, 530 Wh cumulative; eo-server-a=60 Wh interval, 240 Wh cumulative; eo-server-b=20 Wh interval, 290 Wh cumulative
- Relationship families: metering / metered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, energy/total-energy-consumed, relationship/type,peer/id
- Simulator-only metadata: none

### U10-3 - TRAFFIC_BURST

- Description: A sudden traffic burst wakes server-B and sharply increases energy consumption.
- Main state/data: eo-server-a=active; eo-server-b=active; eo-router-a=460 W; eo-router-b=470 W; eo-upstream-meter=360 Wh interval, 890 Wh cumulative; eo-server-a=150 Wh interval, 390 Wh cumulative; eo-server-b=210 Wh interval, 500 Wh cumulative
- Relationship families: metering / metered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, energy/total-energy-consumed, relationship/type,peer/id
- Simulator-only metadata: none

### U10-4 - METERED_INTERVAL_RECORDED

- Description: A new interval records upstream and component energy without changing cumulative semantics.
- Main state/data: eo-router-a=490 W; eo-router-b=470 W; eo-upstream-meter=320 Wh interval, 1210 Wh cumulative; eo-server-a=130 Wh interval, 520 Wh cumulative; eo-server-b=190 Wh interval, 690 Wh cumulative
- Relationship families: metering / metered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, energy/total-energy-consumed, relationship/type,peer/id
- Simulator-only metadata: none

### U10-5 - SLEEP_STATE_VERIFIED

- Description: The low-power component state and its interval measurement are observed together.
- Main state/data: eo-server-a=active; eo-server-b=low-power; eo-router-a=280 W; eo-router-b=420 W; eo-upstream-meter=90 Wh interval, 1300 Wh cumulative; eo-server-a=65 Wh interval, 585 Wh cumulative; eo-server-b=25 Wh interval, 715 Wh cumulative
- Relationship families: metering / metered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, energy/total-energy-consumed, relationship/type,peer/id
- Simulator-only metadata: none

### U10-6 - WAKE_RESPONSE_MEASURED

- Description: A returning workload wakes server-B and produces a distinct energy interval.
- Main state/data: eo-server-a=active; eo-server-b=active; eo-router-a=360 W; eo-router-b=440 W; eo-upstream-meter=240 Wh interval, 1540 Wh cumulative; eo-server-a=110 Wh interval, 695 Wh cumulative; eo-server-b=130 Wh interval, 845 Wh cumulative
- Relationship families: metering / metered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, energy/total-energy-consumed, relationship/type,peer/id
- Simulator-only metadata: none

### U10-7 - RECOVERY_INTERVAL_CONFIRMED

- Description: The recovered service interval is reconciled with its upstream meter relationships.
- Main state/data: eo-router-a=470 W; eo-router-b=475 W; eo-upstream-meter=340 Wh interval, 1880 Wh cumulative; eo-server-a=140 Wh interval, 835 Wh cumulative; eo-server-b=200 Wh interval, 1045 Wh cumulative
- Relationship families: metering / metered-by, enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, energy/total-energy-consumed, relationship/type,peer/id
- Simulator-only metadata: none

## UC 2.11 - Energy Efficiency Network Management

| UC      | Event ID | Event name                         | Relationship families       |
| ------- | -------- | ---------------------------------- | --------------------------- |
| UC 2.11 | U11-0    | INVENTORY_DISCOVERED               | aggregating / aggregated-by |
| UC 2.11 | U11-1    | REALTIME_TELEMETRY_COLLECTED       | aggregating / aggregated-by |
| UC 2.11 | U11-2    | CAPABILITIES_AND_LEGACY_CLASSIFIED | aggregating / aggregated-by |
| UC 2.11 | U11-3    | NETWORK_ENERGY_TREND_AGGREGATED    | aggregating / aggregated-by |
| UC 2.11 | U11-4    | TELEMETRY_FRESHNESS_CHECKED        | aggregating / aggregated-by |
| UC 2.11 | U11-5    | ENERGY_CLASSIFICATION_REVIEWED     | aggregating / aggregated-by |
| UC 2.11 | U11-6    | NETWORK_TREND_VALIDATED            | aggregating / aggregated-by |
| UC 2.11 | U11-7    | MANAGEMENT_VIEW_RECONCILED         | aggregating / aggregated-by |

### U11-0 - INVENTORY_DISCOVERED

- Description: The management view discovers devices and their hardware-correlated energy objects.
- Main state/data: eo-network-energy-aggregator=2100 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: management-stage=inventory; visible-devices=router-A,router-B,router-C

### U11-1 - REALTIME_TELEMETRY_COLLECTED

- Description: Current power observations are collected and associated with network components.
- Main state/data: eo-router-a=420 W; eo-router-b=380 W; eo-router-c=510 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: management-stage=telemetry; historical-view=available

### U11-2 - CAPABILITIES_AND_LEGACY_CLASSIFIED

- Description: Energy-saving capability and legacy status are classified without treating unknown as false.
- Main state/data: eo-router-a=420 W; eo-router-b=380 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: router-A-class=optimized; router-B-class=legacy; unsupported-capability=unknown

### U11-3 - NETWORK_ENERGY_TREND_AGGREGATED

- Description: The manager aggregates energy trends across devices for an operator-level view.
- Main state/data: eo-network-energy-aggregator=1310 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: management-stage=aggregate-trend; aggregation-domain=network

### U11-4 - TELEMETRY_FRESHNESS_CHECKED

- Description: Fresh power observations are checked across the managed router inventory.
- Main state/data: eo-router-a=410 W; eo-router-b=370 W; eo-router-c=500 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: management-stage=freshness-check; telemetry-status=fresh

### U11-5 - ENERGY_CLASSIFICATION_REVIEWED

- Description: Known classifications are retained while unsupported capability remains unknown.
- Main state/data: eo-router-a=410 W; eo-router-b=370 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: router-A-class=optimized; router-B-class=legacy; unsupported-capability=unknown

### U11-6 - NETWORK_TREND_VALIDATED

- Description: The network energy trend is checked against its constituent device observations.
- Main state/data: eo-network-energy-aggregator=1280 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: management-stage=trend-validation; aggregation-domain=network

### U11-7 - MANAGEMENT_VIEW_RECONCILED

- Description: The operator view preserves device readings and controller-derived classifications.
- Main state/data: eo-network-energy-aggregator=1280 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: management-stage=reconciled; classification-source=controller

## UC 2.12 - ISAC-enabled Energy-Aware Smart City Traffic Management

| UC      | Event ID | Event name                   | Relationship families       |
| ------- | -------- | ---------------------------- | --------------------------- |
| UC 2.12 | U12-0    | PEAK_HIGH_RESOLUTION_SENSING | aggregating / aggregated-by |
| UC 2.12 | U12-1    | LOW_TRAFFIC_DETECTED         | aggregating / aggregated-by |
| UC 2.12 | U12-2    | SENSING_LOW_POWER            | aggregating / aggregated-by |
| UC 2.12 | U12-3    | ENERGY_AWARE_TRAFFIC_REROUTE | aggregating / aggregated-by |
| UC 2.12 | U12-4    | CRITICAL_SENSING_PRESERVED   | aggregating / aggregated-by |
| UC 2.12 | U12-5    | TRAFFIC_CONTEXT_CONFIRMED    | aggregating / aggregated-by |
| UC 2.12 | U12-6    | OPTIONAL_SENSING_REDUCED     | aggregating / aggregated-by |
| UC 2.12 | U12-7    | LOW_ENERGY_ROUTE_CONFIRMED   | aggregating / aggregated-by |
| UC 2.12 | U12-8    | CRITICAL_DETECTION_CHECKED   | aggregating / aggregated-by |
| UC 2.12 | U12-9    | SENSING_PROFILE_STABILIZED   | aggregating / aggregated-by |

### U12-0 - PEAK_HIGH_RESOLUTION_SENSING

- Description: High-resolution sensing supports detailed traffic awareness during peak conditions.
- Main state/data: eo-radar-sensor=active; eo-radar-sensor=1350 W; eo-roadside-unit=2200 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: traffic-condition=peak; sensing-mode=high-resolution

### U12-1 - LOW_TRAFFIC_DETECTED

- Description: Sensing identifies a low-traffic context while critical functions remain available.
- Main state/data: eo-radar-sensor=1100 W; eo-roadside-unit=2050 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: traffic-condition=low; critical-sensing=active

### U12-2 - SENSING_LOW_POWER

- Description: Noncritical sensing lowers its resolution while threat detection stays operational.
- Main state/data: eo-radar-sensor=low-power; eo-radar-sensor=620 W; eo-roadside-unit=1650 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: sensing-mode=low-power; critical-sensing=active

### U12-3 - ENERGY_AWARE_TRAFFIC_REROUTE

- Description: Traffic is steered toward lower-energy routes based on local and global conditions.
- Main state/data: eo-roadside-unit=1550 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: traffic-action=energy-aware-reroute; critical-functions=preserved

### U12-4 - CRITICAL_SENSING_PRESERVED

- Description: Critical sensing remains active while optional functions adapt to current conditions.
- Main state/data: eo-radar-sensor=low-power; eo-radar-sensor=650 W; eo-roadside-unit=1580 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: critical-sensing=active; optional-sensing=adaptive

### U12-5 - TRAFFIC_CONTEXT_CONFIRMED

- Description: Traffic context is confirmed before adapting optional sensing work.
- Main state/data: eo-radar-sensor=1180 W; eo-roadside-unit=1980 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: traffic-condition=moderate; critical-sensing=active

### U12-6 - OPTIONAL_SENSING_REDUCED

- Description: Optional sensing uses lower resolution while critical detection remains active.
- Main state/data: eo-radar-sensor=low-power; eo-radar-sensor=780 W; eo-roadside-unit=1740 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: sensing-mode=reduced; critical-sensing=active

### U12-7 - LOW_ENERGY_ROUTE_CONFIRMED

- Description: The selected traffic route reduces energy while preserving critical service functions.
- Main state/data: eo-roadside-unit=1600 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: traffic-action=energy-aware-reroute; critical-functions=preserved

### U12-8 - CRITICAL_DETECTION_CHECKED

- Description: Critical sensing remains available after optional sensing and routing changes.
- Main state/data: eo-radar-sensor=low-power; eo-radar-sensor=640 W; eo-roadside-unit=1580 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: critical-sensing=verified; optional-sensing=adaptive

### U12-9 - SENSING_PROFILE_STABILIZED

- Description: The adaptive sensing profile stabilizes with essential traffic monitoring active.
- Main state/data: eo-radar-sensor=low-power; eo-radar-sensor=650 W; eo-roadside-unit=1590 W
- Relationship families: aggregating / aggregated-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: sensing-mode=adaptive; critical-functions=active

## UC 2.13 - Double Accounting Open issue

| UC      | Event ID | Event name                        | Relationship families                       |
| ------- | -------- | --------------------------------- | ------------------------------------------- |
| UC 2.13 | U13-0    | RAW_MEASUREMENTS                  | metering / metered-by (topology transition) |
| UC 2.13 | U13-1    | TOPOLOGY_DISCOVERED               | metering / metered-by                       |
| UC 2.13 | U13-2    | NEXT_MEASUREMENT_INTERVAL         | metering / metered-by                       |
| UC 2.13 | U13-3    | TOPOLOGY_INCOMPLETE               | metering / metered-by                       |
| UC 2.13 | U13-4    | METERING_PATH_RESTORED            | metering / metered-by                       |
| UC 2.13 | U13-5    | ACCOUNTING_BOUNDARY_REVALIDATED   | metering / metered-by                       |
| UC 2.13 | U13-6    | SERVER_B_METER_LINK_REMOVED       | metering / metered-by                       |
| UC 2.13 | U13-7    | TOPOLOGY_RECONCILIATION_COMPLETED | metering / metered-by                       |

### U13-0 - RAW_MEASUREMENTS

- Description: Measurements exist, but missing topology prevents reliable de-duplication.
- Main state/data: eo-upstream-meter=300 Wh interval; eo-server-a=120 Wh interval; eo-server-b=180 Wh interval
- Relationship families: metering / metered-by (topology transition)
- YANG-visible data: RFC 8348 inventory, source-component-id
- Simulator-only metadata: relationship-change=topology-not-discovered

### U13-1 - TOPOLOGY_DISCOVERED

- Description: Metering relationships now reveal which downstream measurements are already represented upstream.
- Main state/data: eo-upstream-meter=300 Wh interval; eo-server-a=120 Wh interval; eo-server-b=180 Wh interval
- Relationship families: metering / metered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, relationship/type,peer/id
- Simulator-only metadata: none

### U13-2 - NEXT_MEASUREMENT_INTERVAL

- Description: New values prove de-duplication depends on topology rather than numerical equality.
- Main state/data: eo-upstream-meter=340 Wh interval; eo-server-a=140 Wh interval; eo-server-b=190 Wh interval
- Relationship families: metering / metered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, relationship/type,peer/id
- Simulator-only metadata: none

### U13-3 - TOPOLOGY_INCOMPLETE

- Description: A missing relationship makes the energy accounting boundary incomplete again.
- Main state/data: eo-upstream-meter=310 Wh interval; eo-server-a=125 Wh interval; eo-server-b=175 Wh interval
- Relationship families: metering / metered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, relationship/type,peer/id
- Simulator-only metadata: relationship-change=server-B-path-removed

### U13-4 - METERING_PATH_RESTORED

- Description: Restored metering links make the accounting boundary observable again.
- Main state/data: eo-upstream-meter=320 Wh interval; eo-server-a=130 Wh interval; eo-server-b=190 Wh interval
- Relationship families: metering / metered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, relationship/type,peer/id
- Simulator-only metadata: none

### U13-5 - ACCOUNTING_BOUNDARY_REVALIDATED

- Description: The upstream and downstream paths are checked before the next accounting result.
- Main state/data: eo-upstream-meter=330 Wh interval; eo-server-a=140 Wh interval; eo-server-b=190 Wh interval
- Relationship families: metering / metered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, relationship/type,peer/id
- Simulator-only metadata: none

### U13-6 - SERVER_B_METER_LINK_REMOVED

- Description: Removing one meter link marks the boundary incomplete without using value equality.
- Main state/data: eo-upstream-meter=300 Wh interval; eo-server-a=140 Wh interval; eo-server-b=160 Wh interval
- Relationship families: metering / metered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, relationship/type,peer/id
- Simulator-only metadata: relationship-change=server-B-path-removed

### U13-7 - TOPOLOGY_RECONCILIATION_COMPLETED

- Description: Reconciled metering topology restores a defensible accounting boundary.
- Main state/data: eo-upstream-meter=310 Wh interval; eo-server-a=130 Wh interval; eo-server-b=180 Wh interval
- Relationship families: metering / metered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, relationship/type,peer/id
- Simulator-only metadata: accounting-basis=topology

## UC 2.14 - Energy Efficiency Under Power Shortage

| UC      | Event ID | Event name                  | Relationship families |
| ------- | -------- | --------------------------- | --------------------- |
| UC 2.14 | U14-0    | GRID_NORMAL                 | powering / powered-by |
| UC 2.14 | U14-1    | GRID_FAILURE                | powering / powered-by |
| UC 2.14 | U14-2    | BATTERY_OPERATION           | powering / powered-by |
| UC 2.14 | U14-3    | ENERGY_CRITICAL             | powering / powered-by |
| UC 2.14 | U14-4    | GRID_RESTORED               | powering / powered-by |
| UC 2.14 | U14-5    | BACKUP_RESERVE_REVIEWED     | powering / powered-by |
| UC 2.14 | U14-6    | NONCRITICAL_LOAD_SHED       | powering / powered-by |
| UC 2.14 | U14-7    | CRITICAL_SERVICE_STABILIZED | powering / powered-by |
| UC 2.14 | U14-8    | GRID_RETURN_CONFIRMED       | powering / powered-by |
| UC 2.14 | U14-9    | BATTERY_RECHARGE_OBSERVED   | powering / powered-by |

### U14-0 - GRID_NORMAL

- Description: Normal grid power lets every component and service operate without energy restrictions.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-b-non-critical-port=active; eo-router-a=500 W; eo-router-b=400 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=grid; critical-service=active; non-critical-service=active

### U14-1 - GRID_FAILURE

- Description: Grid power fails, so the simulated network switches to its backup energy source.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-b-non-critical-port=active; eo-router-a=480 W; eo-router-b=390 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=battery; battery-level-percent=100; critical-service=active

### U14-2 - BATTERY_OPERATION

- Description: Falling battery capacity triggers energy-saving actions while normal connectivity remains available.
- Main state/data: eo-router-a=active; eo-router-b=low-power; eo-router-b-non-critical-port=off; eo-router-a=420 W; eo-router-b=250 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=battery; battery-level-percent=55; critical-service=active; non-critical-port=disabled

### U14-3 - ENERGY_CRITICAL

- Description: Critical battery levels disable non-essential functions while preserving essential network service.
- Main state/data: eo-router-a=active; eo-router-b=low-power; eo-router-b-non-critical-port=off; eo-router-a=380 W; eo-router-b=200 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=battery; battery-level-percent=15; network-mode=constrained; critical-service=active; non-critical-service=disabled

### U14-4 - GRID_RESTORED

- Description: Grid power returns, restoring normal operation while the backup battery begins recharging.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-b-non-critical-port=active; eo-router-a=500 W; eo-router-b=400 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=grid; battery=charging; critical-service=active; non-critical-service=active

### U14-5 - BACKUP_RESERVE_REVIEWED

- Description: The remaining backup reserve is reviewed while critical connectivity stays active.
- Main state/data: eo-router-a=active; eo-router-b=low-power; eo-router-b-non-critical-port=off; eo-router-a=360 W; eo-router-b=185 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=battery; battery-level-percent=10; critical-service=active

### U14-6 - NONCRITICAL_LOAD_SHED

- Description: Noncritical load remains disabled as the backup reserve continues to fall.
- Main state/data: eo-router-a=active; eo-router-b=low-power; eo-router-b-non-critical-port=off; eo-router-a=350 W; eo-router-b=175 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=battery; battery-level-percent=8; critical-service=active; non-critical-service=disabled

### U14-7 - CRITICAL_SERVICE_STABILIZED

- Description: Essential network service remains active at the minimum demonstrated battery reserve.
- Main state/data: eo-router-a=active; eo-router-b=low-power; eo-router-b-non-critical-port=off; eo-router-a=340 W; eo-router-b=165 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=battery; battery-level-percent=5; critical-service=active

### U14-8 - GRID_RETURN_CONFIRMED

- Description: Grid power is confirmed before the backup source is released.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-b-non-critical-port=active; eo-router-a=480 W; eo-router-b=380 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=grid; critical-service=active

### U14-9 - BATTERY_RECHARGE_OBSERVED

- Description: The restored grid supplies the network while the backup battery recharges.
- Main state/data: eo-router-a=active; eo-router-b=active; eo-router-b-non-critical-port=active; eo-router-a=510 W; eo-router-b=410 W
- Relationship families: powering / powered-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: power-source=grid; battery=charging; critical-service=active

## UC 2.15 - Energy-Efficient Management of Distributed AI Training Workloads

| UC      | Event ID | Event name                   | Relationship families |
| ------- | -------- | ---------------------------- | --------------------- |
| UC 2.15 | U15-0    | TRAINING_FULL_CLUSTER        | none                  |
| UC 2.15 | U15-1    | ENERGY_AWARE_SCHEDULE_WINDOW | none                  |
| UC 2.15 | U15-2    | DATA_TRANSFER_OPTIMIZED      | none                  |
| UC 2.15 | U15-3    | ACTIVE_NODES_ADJUSTED        | none                  |
| UC 2.15 | U15-4    | TRAINING_WINDOW_RESERVED     | none                  |
| UC 2.15 | U15-5    | TRANSFER_VOLUME_REDUCED      | none                  |
| UC 2.15 | U15-6    | COMPUTE_LOCALITY_CONFIRMED   | none                  |
| UC 2.15 | U15-7    | CLUSTER_CAPACITY_REBALANCED  | none                  |

### U15-0 - TRAINING_FULL_CLUSTER

- Description: Active training nodes exchange East-West data across the cluster fabric.
- Main state/data: eo-ai-node-1=active; eo-ai-node-2=active; eo-ai-node-1=620 W; eo-ai-node-2=610 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: east-west-traffic-gb=800; schedule-window=standard

### U15-1 - ENERGY_AWARE_SCHEDULE_WINDOW

- Description: The controller selects a lower-energy scheduling window for the training workload.
- Main state/data: eo-ai-cluster-energy-aggregator=1320 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: schedule-window=lower-energy-period; energy-price=simulated-low

### U15-2 - DATA_TRANSFER_OPTIMIZED

- Description: Compression and data locality reduce East-West transfers without defining a training protocol.
- Main state/data: eo-ai-node-1=570 W; eo-ai-node-2=550 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: compression=enabled; east-west-traffic-gb=480; data-placement=near-compute

### U15-3 - ACTIVE_NODES_ADJUSTED

- Description: Active-node allocation follows training progress while preserving workload capacity.
- Main state/data: eo-ai-node-2=low-power; eo-ai-node-1=570 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: active-nodes=1; resource-co-location=enabled

### U15-4 - TRAINING_WINDOW_RESERVED

- Description: The workload is assigned a lower-energy window before its next training stage.
- Main state/data: eo-ai-cluster-energy-aggregator=1280 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: schedule-window=lower-energy-period; reservation=confirmed

### U15-5 - TRANSFER_VOLUME_REDUCED

- Description: Compression reduces East-West transfer volume while both training nodes remain available.
- Main state/data: eo-ai-node-1=active; eo-ai-node-2=active; eo-ai-node-1=560 W; eo-ai-node-2=545 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: compression=enabled; east-west-traffic-gb=420

### U15-6 - COMPUTE_LOCALITY_CONFIRMED

- Description: Training data is placed near compute to avoid unnecessary cluster transfers.
- Main state/data: eo-ai-node-1=550 W; eo-ai-node-2=535 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: data-placement=near-compute; cross-node-transfer=reduced

### U15-7 - CLUSTER_CAPACITY_REBALANCED

- Description: Active-node allocation is rebalanced while preserving the configured workload capacity.
- Main state/data: eo-ai-node-2=low-power; eo-ai-node-1=560 W
- Relationship families: none
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power
- Simulator-only metadata: active-nodes=1; resource-co-location=enabled

## UC 2.16 - Network-level Cross Layer Energy Saving

| UC      | Event ID | Event name                        | Relationship families |
| ------- | -------- | --------------------------------- | --------------------- |
| UC 2.16 | U16-0    | MULTILAYER_NORMAL                 | enabling / enabled-by |
| UC 2.16 | U16-1    | IP_LINECARD_SLEEP_REQUEST         | enabling / enabled-by |
| UC 2.16 | U16-2    | UNDERLAY_DEPENDENCIES_COORDINATED | enabling / enabled-by |
| UC 2.16 | U16-3    | MULTILAYER_LOW_POWER_STABLE       | enabling / enabled-by |
| UC 2.16 | U16-4    | MULTILAYER_RESTORED               | enabling / enabled-by |
| UC 2.16 | U16-5    | DEPENDENCY_SET_VALIDATED          | enabling / enabled-by |
| UC 2.16 | U16-6    | UNDERLAY_SLEEP_WINDOW_CONFIRMED   | enabling / enabled-by |
| UC 2.16 | U16-7    | QOS_DEPENDENCY_VERIFIED           | enabling / enabled-by |
| UC 2.16 | U16-8    | LOW_POWER_DEPENDENCIES_STABLE     | enabling / enabled-by |
| UC 2.16 | U16-9    | RESTORE_DEPENDENCY_CONFIRMED      | enabling / enabled-by |

### U16-0 - MULTILAYER_NORMAL

- Description: IP overlay and transport underlay carry normal service traffic.
- Main state/data: eo-router-a=active; eo-transport-module=active; eo-router-a=500 W; eo-transport-module=820 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: network-layers=L3-overlay,L0-L2-underlay

### U16-1 - IP_LINECARD_SLEEP_REQUEST

- Description: An IP line-card sleep request is checked against dependent underlay resources.
- Main state/data: eo-router-a-linecard-1=low-power; eo-router-a=420 W; eo-transport-module=760 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: request=linecard-sleep; dependency-check=required

### U16-2 - UNDERLAY_DEPENDENCIES_COORDINATED

- Description: Underlay dependencies are coordinated before any shared resource enters low power.
- Main state/data: eo-transport-module=low-power; eo-router-a=390 W; eo-transport-module=650 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: coordination=overlay-underlay; service-qos=preserved

### U16-3 - MULTILAYER_LOW_POWER_STABLE

- Description: Coordinated low-power states remain stable while cross-layer service dependencies hold.
- Main state/data: eo-router-a-linecard-1=low-power; eo-transport-module=low-power; eo-router-a=360 W; eo-transport-module=610 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: network-layers=coordinated-low-power

### U16-4 - MULTILAYER_RESTORED

- Description: Restoring transport and IP resources returns the multilayer service to normal operation.
- Main state/data: eo-router-a-linecard-1=active; eo-transport-module=active; eo-router-a=500 W; eo-transport-module=820 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: network-layers=restored; service-qos=preserved

### U16-5 - DEPENDENCY_SET_VALIDATED

- Description: Overlay and underlay dependencies are validated before another low-power transition.
- Main state/data: eo-router-a=470 W; eo-transport-module=790 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: dependency-check=passed; network-layers=L3-overlay,L0-L2-underlay

### U16-6 - UNDERLAY_SLEEP_WINDOW_CONFIRMED

- Description: The underlay sleep window is coordinated with the dependent IP function.
- Main state/data: eo-transport-module=low-power; eo-router-a=430 W; eo-transport-module=720 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: coordination=overlay-underlay; sleep-window=confirmed

### U16-7 - QOS_DEPENDENCY_VERIFIED

- Description: Quality of service remains within the simulated constraint during coordinated savings.
- Main state/data: eo-router-a=400 W; eo-transport-module=680 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: service-qos=preserved; dependency-check=passed

### U16-8 - LOW_POWER_DEPENDENCIES_STABLE

- Description: Shared resources remain in low power while their dependent service stays available.
- Main state/data: eo-router-a-linecard-1=low-power; eo-transport-module=low-power; eo-router-a=370 W; eo-transport-module=630 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: network-layers=coordinated-low-power; service-qos=preserved

### U16-9 - RESTORE_DEPENDENCY_CONFIRMED

- Description: Transport and IP resources recover together before normal service is declared.
- Main state/data: eo-router-a-linecard-1=active; eo-transport-module=active; eo-router-a=500 W; eo-transport-module=820 W
- Relationship families: enabling / enabled-by
- YANG-visible data: RFC 8348 inventory, source-component-id, power-state/oper, power/instantaneous-power, relationship/type,peer/id
- Simulator-only metadata: network-layers=restored; service-qos=preserved

