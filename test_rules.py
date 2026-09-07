"""
AquaGuard - Unit tests for the rule-based detection engine.
Run with: python -m unittest test_rules.py -v
No extra dependencies required (uses stdlib unittest).
"""

import unittest
from rules import detect_anomalies, get_summary, NIGHT_HOURS
from data_generator import BASELINE_FLOW


def make_reading(zone, hour, flow_rate, day="2024-01-01"):
    return {
        "zone": zone,
        "timestamp": f"{day} {hour:02d}:00",
        "flow_rate": flow_rate,
    }


class TestLeakDetection(unittest.TestCase):
    def test_flags_high_night_flow_as_leak(self):
        zone = "Zone-B (Admin Block)"
        # Baseline 60 -> expected night flow ~15, leak threshold ~24
        readings = [make_reading(zone, 3, 40)]
        alerts = detect_anomalies(readings)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["type"], "Leak")

    def test_normal_night_flow_not_flagged(self):
        zone = "Zone-B (Admin Block)"
        readings = [make_reading(zone, 3, 12)]  # below threshold
        alerts = detect_anomalies(readings)
        self.assertEqual(len(alerts), 0)


class TestSpikeDetection(unittest.TestCase):
    def test_flags_flow_above_2x_baseline(self):
        zone = "Zone-C (Canteen)"
        baseline = BASELINE_FLOW[zone]
        readings = [make_reading(zone, 14, baseline * 2.5)]
        alerts = detect_anomalies(readings)
        self.assertTrue(any(a["type"] == "Spike" for a in alerts))

    def test_normal_daytime_flow_not_flagged(self):
        zone = "Zone-C (Canteen)"
        baseline = BASELINE_FLOW[zone]
        readings = [make_reading(zone, 14, baseline * 1.1)]
        alerts = detect_anomalies(readings)
        self.assertEqual(len(alerts), 0)


class TestTheftDetection(unittest.TestCase):
    def test_flags_off_hour_high_flow(self):
        zone = "Zone-D (Sports Complex)"
        baseline = BASELINE_FLOW[zone]
        readings = [make_reading(zone, 23, baseline * 2)]
        alerts = detect_anomalies(readings)
        self.assertTrue(any(a["type"] == "Theft/Tampering" for a in alerts))

    def test_low_off_hour_flow_not_flagged(self):
        zone = "Zone-D (Sports Complex)"
        readings = [make_reading(zone, 23, 5)]
        alerts = detect_anomalies(readings)
        self.assertEqual(len(alerts), 0)


class TestSummary(unittest.TestCase):
    def test_summary_counts_match_alerts(self):
        zone = "Zone-B (Admin Block)"
        readings = [make_reading(zone, 3, 40), make_reading(zone, 4, 40)]
        alerts = detect_anomalies(readings)
        summary = get_summary(alerts, readings)
        self.assertEqual(summary["total_alerts"], len(alerts))
        self.assertEqual(summary["total_readings"], len(readings))

    def test_empty_readings_gives_zero_alerts(self):
        alerts = detect_anomalies([])
        summary = get_summary(alerts, [])
        self.assertEqual(summary["total_alerts"], 0)
        self.assertEqual(summary["zones_affected"], 0)


class TestNightHoursConfig(unittest.TestCase):
    def test_night_hours_cover_expected_range(self):
        for h in [22, 23, 0, 1, 2, 3, 4, 5]:
            self.assertIn(h, NIGHT_HOURS)
        for h in [8, 12, 18]:
            self.assertNotIn(h, NIGHT_HOURS)


if __name__ == "__main__":
    unittest.main()
