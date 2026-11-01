# Canonical Demo Network

`DEMO-NETWORK-1` is one stable logical network composed of 6 reusable sub-topologies.

| Topology | Name | Device instances | Energy Objects | Relationship profiles |
| --- | --- | --- | ---: | --- |
| T1 CORE (T1-fixed-network) | Fixed network | Router A, Router B, Router C | 7 | uc10, network-management |
| T2 AIR (T2-wlan-poe) | WLAN and PoE | WLAN access system 1, WLAN access point 2 | 7 | wlan |
| T3 POWER (T3-power-infrastructure) | Power infrastructure | PDU and metering system, Legacy metered device, Grid power source, Backup power source, Router A, Router B | 14 | pdu-indirect, grid-source, battery-source, uc13-full, uc13-partial |
| T4 BACKHAUL (T4-wireless-transport) | Wireless transport | Microwave site 1, Transport site 1, Multilayer controller, Router A | 9 | cross-layer |
| T5 EDGE (T5-edge-compute) | Edge and compute | PDU and metering system, Cross-domain controller, Access domain controller, Transport domain controller, Core domain controller, Network management controller, Video service, AI training cluster, AI training node 1, AI training node 2 | 17 | cross-domain, network-management, uc10, uc13-full, uc13-partial |
| T6 CITY (T6-isac-smart-city) | ISAC and smart city | Smart city controller, Smart city roadside site 1 | 5 | isac |

Sub-topologies may share a stable device instance; the UC mapping selects a primary view and optional supporting views without cloning the device inventory.
RFC 8348 containment and GREEN Energy Object relationships are modeled separately. The topology registry supplies stable identities; event definitions supply only dynamic overlays.
