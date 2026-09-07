"""
AquaGuard - Sample Water Meter Data Generator
Generates realistic synthetic flow-meter readings for demo purposes.
Zones simulate different areas of a campus/municipality water network.
"""

import random
from datetime import datetime, timedelta

ZONES = ["Zone-A (Hostel)", "Zone-B (Admin Block)", "Zone-C (Canteen)",
         "Zone-D (Sports Complex)", "Zone-E (Residential)"]

# Baseline average flow rate per zone in liters/hour (normal usage pattern)
BASELINE_FLOW = {
    "Zone-A (Hostel)": 120,
    "Zone-B (Admin Block)": 60,
    "Zone-C (Canteen)": 90,
    "Zone-D (Sports Complex)": 40,
    "Zone-E (Residential)": 100,
}


def generate_readings(hours=72, inject_anomalies=True):
    """
    Generates hourly flow readings for each zone over `hours` hours.
    Returns a list of dicts: {zone, timestamp, flow_rate}
    Injects a leak, a spike, and a theft-pattern anomaly for demo purposes.
    """
    readings = []
    start_time = datetime.now() - timedelta(hours=hours)

    for zone in ZONES:
        base = BASELINE_FLOW[zone]
        for h in range(hours):
            ts = start_time + timedelta(hours=h)
            hour_of_day = ts.hour

            # Normal day/night usage variation (lower flow at night)
            night_factor = 0.25 if (hour_of_day <= 5 or hour_of_day >= 22) else 1.0
            noise = random.uniform(-0.15, 0.15)
            flow = round(base * night_factor * (1 + noise), 1)

            readings.append({
                "zone": zone,
                "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
                "flow_rate": flow
            })

    if inject_anomalies:
        _inject_leak(readings)
        _inject_spike(readings)
        _inject_theft(readings)

    return readings


def _inject_leak(readings):
    """Simulate a leak: sustained non-zero flow during night hours (should be ~0)."""
    target_zone = "Zone-B (Admin Block)"
    count = 0
    for r in readings:
        if r["zone"] == target_zone:
            hour = int(r["timestamp"].split(" ")[1].split(":")[0])
            if 1 <= hour <= 5 and count < 6:
                r["flow_rate"] = round(random.uniform(35, 45), 1)  # should be near 0 at night
                count += 1


def _inject_spike(readings):
    """Simulate a sudden spike: usage more than 2x average for a few hours."""
    target_zone = "Zone-C (Canteen)"
    matches = [r for r in readings if r["zone"] == target_zone]
    for r in matches[-5:-2]:
        r["flow_rate"] = round(BASELINE_FLOW[target_zone] * random.uniform(2.5, 3.2), 1)


def _inject_theft(readings):
    """Simulate theft/tampering: unexpected flow in an unmetered/low-use zone
    during off-peak hours.

    FIX: scans for night-hour readings by their actual hour (like _inject_leak
    does), instead of grabbing a fixed positional slice near the end of the
    dataset. The old version only injected the anomaly if that slice happened
    to land in the 22:00-04:00 window, which depends on what time of day the
    script is run - so the Theft/Tampering alert could randomly go missing
    from a demo. This version always finds 4 genuine off-hour readings and
    is reliable no matter when app.py is started.
    """
    target_zone = "Zone-D (Sports Complex)"
    count = 0
    for r in readings:
        if r["zone"] == target_zone:
            hour = int(r["timestamp"].split(" ")[1].split(":")[0])
            if (22 <= hour or hour <= 4) and count < 4:
                r["flow_rate"] = round(random.uniform(80, 110), 1)  # abnormal for off-hours
                count += 1
