"""
AquaGuard - AI-Based Water Leak & Theft Detection System
1M1B AI for Sustainability Virtual Internship Project
SDG 6: Clean Water and Sanitation

A rule-based anomaly detection system that monitors water flow data
across zones and flags leaks, spikes, and theft/tampering patterns.
"""

from flask import Flask, render_template, jsonify
from data_generator import generate_readings, ZONES
from rules import detect_anomalies, get_summary

app = Flask(__name__)

# Generate one sample dataset at startup (simulates 72 hours of meter data)
READINGS = generate_readings(hours=72, inject_anomalies=True)
ALERTS = detect_anomalies(READINGS)
SUMMARY = get_summary(ALERTS, READINGS)


@app.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        alerts=ALERTS,
        summary=SUMMARY,
        zones=ZONES,
    )


@app.route("/api/refresh")
def refresh():
    """Regenerates a fresh dataset and re-runs detection (for demo purposes)."""
    global READINGS, ALERTS, SUMMARY
    READINGS = generate_readings(hours=72, inject_anomalies=True)
    ALERTS = detect_anomalies(READINGS)
    SUMMARY = get_summary(ALERTS, READINGS)
    return jsonify({"summary": SUMMARY, "alerts": ALERTS})


@app.route("/api/alerts")
def api_alerts():
    return jsonify(ALERTS)


@app.route("/api/zone/<zone_name>")
def zone_readings(zone_name):
    """Returns hourly readings for a specific zone (for charting)."""
    data = [r for r in READINGS if r["zone"] == zone_name]
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
