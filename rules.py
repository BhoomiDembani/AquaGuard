"""
AquaGuard - Rule-Based Anomaly Detection Engine
Applies transparent, explainable rules to flag leaks, spikes, and theft
patterns in water flow data. No black-box ML - every flag has a clear reason.
"""

from collections import defaultdict
from data_generator import BASELINE_FLOW


NIGHT_HOURS = set(range(0, 6)) | {22, 23}  # 10 PM - 6 AM considered low-usage hours

# Thresholds (tunable) - kept simple and explainable per Responsible AI guidelines
NIGHT_FLOW_FACTOR = 0.25              # expected night flow = this fraction of zone baseline
LEAK_MARGIN = 1.6                     # flow > (expected night flow * this margin) = possible leak
SPIKE_MULTIPLIER = 2.0                # 2x baseline = spike
THEFT_OFFHOUR_MULTIPLIER = 1.3        # flow > baseline * this, during off-hours = suspicious


def _hour_of(ts):
    return int(ts.split(" ")[1].split(":")[0])


def detect_anomalies(readings):
    """
    Runs all rule checks against readings and returns a list of alerts.
    Each alert: {zone, timestamp, flow_rate, type, severity, reason}
    """
    alerts = []
    alerts.extend(_check_leaks(readings))
    alerts.extend(_check_spikes(readings))
    alerts.extend(_check_theft(readings))

    # Sort most recent first
    alerts.sort(key=lambda a: a["timestamp"], reverse=True)
    return alerts


def _check_leaks(readings):
    """Rule: flow well above a zone's expected night-time level suggests a leak."""
    alerts = []
    for r in readings:
        if _hour_of(r["timestamp"]) in NIGHT_HOURS:
            baseline = BASELINE_FLOW.get(r["zone"], 0)
            expected_night_flow = baseline * NIGHT_FLOW_FACTOR
            threshold = expected_night_flow * LEAK_MARGIN
            if baseline and r["flow_rate"] > threshold:
                alerts.append({
                    "zone": r["zone"],
                    "timestamp": r["timestamp"],
                    "flow_rate": r["flow_rate"],
                    "type": "Leak",
                    "severity": "High",
                    "reason": (f"Flow of {r['flow_rate']} L/hr detected during night hours, well "
                               f"above this zone's expected night flow of ~{round(expected_night_flow, 1)} "
                               f"L/hr. Likely a leak since no significant usage is expected at this time.")
                })
    return alerts


def _check_spikes(readings):
    """Rule: flow more than SPIKE_MULTIPLIER times the zone's baseline = spike."""
    alerts = []
    for r in readings:
        baseline = BASELINE_FLOW.get(r["zone"], 0)
        if baseline and r["flow_rate"] > baseline * SPIKE_MULTIPLIER:
            alerts.append({
                "zone": r["zone"],
                "timestamp": r["timestamp"],
                "flow_rate": r["flow_rate"],
                "type": "Spike",
                "severity": "Medium",
                "reason": (f"Flow of {r['flow_rate']} L/hr is over {SPIKE_MULTIPLIER}x the "
                           f"normal baseline of {baseline} L/hr for this zone. Possible burst "
                           f"pipe, faulty valve, or unusual usage event.")
            })
    return alerts


def _check_theft(readings):
    """Rule: flow far above baseline during off-hours = possible tampering/theft.
    Distinct from the leak check: this catches large, sudden off-hour draws rather
    than small sustained ones."""
    alerts = []
    for r in readings:
        hour = _hour_of(r["timestamp"])
        baseline = BASELINE_FLOW.get(r["zone"], 0)
        if hour in NIGHT_HOURS and baseline:
            if r["flow_rate"] > baseline * THEFT_OFFHOUR_MULTIPLIER:
                alerts.append({
                    "zone": r["zone"],
                    "timestamp": r["timestamp"],
                    "flow_rate": r["flow_rate"],
                    "type": "Theft/Tampering",
                    "severity": "High",
                    "reason": (f"Flow of {r['flow_rate']} L/hr in a typically low-use zone "
                               f"during off-peak hours ({hour}:00), exceeding {baseline} L/hr "
                               f"daytime baseline. Pattern is consistent with unauthorized "
                               f"tapping or meter tampering.")
                })
    return alerts


def get_summary(alerts, readings):
    """Computes dashboard summary stats."""
    by_type = defaultdict(int)
    by_severity = defaultdict(int)
    for a in alerts:
        by_type[a["type"]] += 1
        by_severity[a["severity"]] += 1

    total_flow = sum(r["flow_rate"] for r in readings)
    zones_affected = len(set(a["zone"] for a in alerts))

    # Rough estimated water loss from flagged anomalies (liters)
    estimated_loss = sum(a["flow_rate"] for a in alerts if a["type"] in ("Leak", "Theft/Tampering"))

    return {
        "total_alerts": len(alerts),
        "by_type": dict(by_type),
        "by_severity": dict(by_severity),
        "zones_affected": zones_affected,
        "estimated_water_loss_liters": round(estimated_loss, 1),
        "total_readings": len(readings),
    }
