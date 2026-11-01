# Energy Object Observability

Classes describe evidence in the deterministic event catalog, not new YANG leaves. Display-only `UNKNOWN` means applicable but absent from the current observation; `N/A` means the observability profile intentionally does not apply the field. Numeric zero remains the measured value `0`.

| Device ID | Energy Object ID | Hardware component | Class | Power evidence | State evidence | Energy evidence | Relationship evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `pdu-1` | `eo-upstream-meter` | `upstream-meter` | `TOPOLOGY_ONLY` | not observed | not observed | observed | defined |
| `pdu-1` | `eo-server-a` | `server-A` | `STATE_ONLY` | not observed | observed | observed | defined |
| `pdu-1` | `eo-server-b` | `server-B` | `STATE_ONLY` | not observed | observed | observed | defined |
| `router-A` | `eo-router-a` | `router-A` | `FULL` | observed | observed | not observed | defined |
| `router-A` | `eo-router-a-linecard-1` | `linecard-1` | `FULL` | observed | observed | not observed | defined |
| `router-A` | `eo-router-a-linecard-2` | `linecard-2` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `router-B` | `eo-router-b` | `router-B` | `FULL` | observed | observed | not observed | defined |
| `router-B` | `eo-router-b-non-critical-port` | `non-critical-port` | `STATE_ONLY` | not observed | observed | not observed | not defined |
| `pdu-1` | `eo-pdu-1` | `pdu-1` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `pdu-1` | `eo-pdu-outlet-1` | `pdu-outlet-1` | `POWER_ONLY` | observed | not observed | not observed | defined |
| `ai-training-node-1` | `eo-ai-node-1-nic-1` | `ai-node-1-nic` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `legacy-device-1` | `eo-legacy-device` | `legacy-device` | `TOPOLOGY_ONLY` | not observed | not observed | not observed | defined |
| `wlan-1` | `eo-poe-switch` | `poe-switch` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `wlan-1` | `eo-poe-port-ap1` | `poe-port-ap1` | `FULL` | observed | observed | not observed | defined |
| `wlan-1` | `eo-ap-1` | `ap-1` | `FULL` | observed | observed | not observed | defined |
| `wlan-2` | `eo-ap-2` | `ap-2` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `wlan-1` | `eo-ap-baseband` | `ap-baseband` | `TOPOLOGY_ONLY` | not observed | not observed | not observed | defined |
| `wlan-1` | `eo-ap-radio-24` | `ap-radio-24` | `STATE_ONLY` | not observed | observed | not observed | defined |
| `wlan-1` | `eo-ap-radio-5` | `ap-radio-5` | `STATE_ONLY` | not observed | observed | not observed | defined |
| `cross-domain-controller` | `eo-domain-energy-aggregator` | `domain-energy-aggregator` | `POWER_ONLY` | observed | not observed | not observed | defined |
| `access-domain-controller` | `eo-access-domain` | `access-domain` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `transport-domain-controller` | `eo-transport-domain` | `transport-domain` | `TOPOLOGY_ONLY` | not observed | not observed | not observed | defined |
| `core-domain-controller` | `eo-core-domain` | `core-domain` | `TOPOLOGY_ONLY` | not observed | not observed | not observed | defined |
| `network-controller` | `eo-network-energy-aggregator` | `network-energy-aggregator` | `POWER_ONLY` | observed | not observed | not observed | defined |
| `router-C` | `eo-router-c` | `router-C` | `POWER_ONLY` | observed | not observed | not observed | defined |
| `smart-city-controller` | `eo-isac-energy-aggregator` | `isac-energy-aggregator` | `TOPOLOGY_ONLY` | not observed | not observed | not observed | defined |
| `smart-city-site-1` | `eo-roadside-unit` | `roadside-unit-1` | `POWER_ONLY` | observed | not observed | not observed | defined |
| `smart-city-site-1` | `eo-radar-sensor` | `radar-sensor-1` | `FULL` | observed | observed | not observed | defined |
| `smart-city-site-1` | `eo-isac-transceiver` | `isac-transceiver-1` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `smart-city-controller` | `eo-city-traffic-controller` | `city-traffic-controller` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `microwave-site-1` | `eo-wireless-link-1` | `wireless-link-1` | `FULL` | observed | observed | not observed | not defined |
| `video-service` | `eo-video-origin-1` | `video-origin-1` | `POWER_ONLY` | observed | not observed | not observed | not defined |
| `video-service` | `eo-video-cache-1` | `video-cache-1` | `POWER_ONLY` | observed | not observed | not observed | not defined |
| `ai-training-cluster` | `eo-ai-cluster-energy-aggregator` | `ai-cluster-energy-aggregator` | `POWER_ONLY` | observed | not observed | not observed | not defined |
| `ai-training-node-1` | `eo-ai-node-1` | `ai-node-1` | `FULL` | observed | observed | not observed | not defined |
| `ai-training-node-2` | `eo-ai-node-2` | `ai-node-2` | `FULL` | observed | observed | not observed | not defined |
| `ai-training-cluster` | `eo-ai-fabric` | `ai-fabric` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `multilayer-controller` | `eo-ip-overlay` | `ip-overlay` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `multilayer-controller` | `eo-transport-underlay` | `transport-underlay` | `UNOBSERVED` | not observed | not observed | not observed | not defined |
| `transport-site-1` | `eo-transport-module` | `transport-module` | `FULL` | observed | observed | not observed | defined |
| `multilayer-controller` | `eo-dependent-ip-function` | `dependent-ip-function` | `TOPOLOGY_ONLY` | not observed | not observed | not observed | defined |
| `router-A` | `eo-switch-fabric` | `switch-fabric` | `TOPOLOGY_ONLY` | not observed | not observed | not observed | defined |
| `power-grid` | `eo-grid-source` | `grid-source` | `TOPOLOGY_ONLY` | not observed | not observed | not observed | defined |
| `power-backup` | `eo-backup-battery` | `backup-battery` | `TOPOLOGY_ONLY` | not observed | not observed | not observed | defined |

Class semantics: `FULL` has event evidence of both instantaneous Power and power State; `POWER_ONLY` has Power evidence; `STATE_ONLY` has State evidence; `TOPOLOGY_ONLY` has interval/cumulative Energy or relationship evidence but no Power/State evidence; `UNOBSERVED` has no event measurement, state, or relationship evidence beyond inventory identity.

Counts: FULL=10, POWER_ONLY=8, STATE_ONLY=5, TOPOLOGY_ONLY=10, UNOBSERVED=11
