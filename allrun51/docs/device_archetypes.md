# Device Archetypes and Instances

Archetypes define reusable device classes; instances provide stable `device_id` values. Hardware Components and Energy Objects remain separate identities below those instances.

| Archetype | Name | Component roles | Device instances |
| --- | --- | --- | --- |
| fixed-router | Fixed-network router | chassis, switch-fabric, linecard, port | router-A, router-B, router-C |
| wlan-access | WLAN and PoE access system | poe-switch, poe-port, access-point, baseband, radio | wlan-1, wlan-2 |
| power-system | Power infrastructure and metering endpoint | grid-source, battery, pdu, outlet, metered-load | legacy-device-1, pdu-1, power-backup, power-grid |
| wireless-transport | Wireless transport system | wireless-link, transport-module, underlay, ip-function | microwave-site-1, transport-site-1 |
| compute-node | Compute node or cluster | server, server-nic, ai-node, fabric, cluster-aggregator | ai-training-cluster, ai-training-node-1, ai-training-node-2 |
| service-appliance | Media service or logical controller | video-origin, cache, domain-aggregator, controller | access-domain-controller, core-domain-controller, cross-domain-controller, multilayer-controller, network-controller, smart-city-controller, transport-domain-controller, video-service |
| isac-roadside-unit | ISAC roadside unit | roadside-unit, radar-sensor, transceiver | smart-city-site-1 |

UC scenarios never redefine or rename a device instance.
