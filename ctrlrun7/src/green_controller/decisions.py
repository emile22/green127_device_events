from __future__ import annotations

from typing import Any

RECOMMENDATIONS = {
    "UC 2.1": "Keep the legacy baseline labeled with its source; compare only when a measured value and baseline provenance are both available.",
    "UC 2.2": "If traffic is low and service continuity is confirmed, evaluate traffic concentration and low-power eligibility; do not infer traffic from power alone.",
    "UC 2.5": "Use the explicitly related external meter as the observation source for an uninstrumented target; retain direct target measurement as unknown.",
    "UC 2.6": "Normalize domain inputs only when units and intervals are compatible; preserve the contributing domains and boundary context.",
    "UC 2.7": "Consider a lower throughput/power profile only when current traffic telemetry and service constraints are available.",
    "UC 2.8": "Compare delivery and cache alternatives using observed energy data; do not assume a control protocol that is not represented.",
    "UC 2.9": "Select an AP mode only after checking coverage and recovery constraints; preserve the observed radio, AP, and PoE states.",
    "UC 2.10": "Recommend sleep/wake only from compatible interval measurements; treat cumulative counters without interval semantics as insufficient.",
    "UC 2.11": "Keep capability classifications and telemetry history in the controller view; preserve unknown as unknown.",
    "UC 2.12": "Preserve critical sensing while evaluating lower-power sensing or routing alternatives.",
    "UC 2.13": "Mark an accounting value authoritative only when explicit metering topology covers the complete boundary.",
    "UC 2.14": "Preserve essential service and prioritize non-critical reduction when backup-energy evidence supports it.",
    "UC 2.15": "Evaluate lower-energy scheduling and data locality while preserving workload-capacity constraints.",
    "UC 2.16": "Verify overlay/underlay dependencies and QoS constraints before recommending a coordinated low-power transition.",
}


def recommendations_for_all_use_cases() -> list[dict[str, Any]]:
    return [
        {
            "uc": uc,
            "recommendation": recommendation,
            "execution_status": "prepared-only; no device operation performed",
        }
        for uc, recommendation in RECOMMENDATIONS.items()
    ]
