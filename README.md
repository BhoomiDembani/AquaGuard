# AquaGuard — AI-Based Water Leak & Theft Detection System

**1M1B AI for Sustainability Virtual Internship** (IBM SkillsBuild & AICTE)

## Project Description
- **SDG Alignment:** SDG 6 (Clean Water and Sanitation), secondary SDG 9 (Industry, Innovation and Infrastructure)
- **Problem Statement:** How might we use AI to detect abnormal water usage patterns (leaks, theft, tampering) so that municipal and campus water systems can become more sustainable and secure?
- **AI Solution Overview:** A transparent, rule-based anomaly detection engine that continuously monitors zone-level water flow data and flags three anomaly types:
  - **Leak** — sustained abnormal flow during night hours when usage should be near zero
  - **Spike** — flow rate more than 2x a zone's normal baseline
  - **Theft/Tampering** — large, unexpected flow in a low-traffic zone during off-peak hours
- **Target Users:** Municipal water utility operators, campus facilities management teams, housing societies
- **Expected Impact:** Faster leak/theft detection → reduced water loss, lower utility costs, and more sustainable water infrastructure management

## Responsible AI Considerations
- **Fairness:** Detection rules apply uniformly to every zone — no zone is pre-labeled as "high risk."
- **Transparency:** Every alert includes a plain-language reason and the exact threshold that was crossed. No black-box scoring.
- **Ethics:** The system only flags anomalies for human review; it does not take autonomous action (e.g., automatically shutting off supply).
- **Privacy:** Works only on zone-level aggregate flow data — no individual household or personal usage data is collected.

## How It Works (Prototype)
1. `data_generator.py` simulates 72 hours of hourly water-meter readings across 5 zones (hostel, admin block, canteen, sports complex, residential), including realistic day/night usage patterns, and injects one leak, one spike, and one theft/tampering event for demo purposes.
2. `rules.py` is the rule-based detection engine — three independent, explainable rule checks (leak, spike, theft) run against the readings.
3. `app.py` is the Flask web server exposing the dashboard and a `/api/refresh` endpoint to regenerate data live.
4. `templates/dashboard.html` + `static/style.css` render a dark-themed monitoring dashboard: summary cards, an alerts table with severity badges, a per-zone flow trend chart (Chart.js), and the Responsible AI section.

## Running Locally
```bash
pip install -r requirements.txt
python app.py
```
Then open **http://127.0.0.1:5000** in your browser.

Click **"↻ Refresh Data"** on the dashboard to regenerate a new simulated dataset and re-run detection live.

## Tuning Detection Thresholds
All thresholds live at the top of `rules.py` and are intentionally simple and explainable (no hidden ML weights):
- `NIGHT_FLOW_FACTOR` — expected fraction of daytime baseline flow during night hours
- `LEAK_MARGIN` — how far above expected night flow counts as a leak
- `SPIKE_MULTIPLIER` — how many times baseline counts as a spike
- `THEFT_OFFHOUR_MULTIPLIER` — how many times baseline during off-hours counts as suspicious

## Testing
Basic unit tests cover all three detection rules and the summary aggregator (no extra dependencies, uses Python's built-in `unittest`):
```bash
python -m unittest test_rules.py -v
```

## Limitations & Future Work
- **Rule-based, not learned:** thresholds are hand-set and explainable, but a real deployment would benefit from a statistical baseline (e.g. per-zone rolling mean/std) that adapts to seasonal or academic-calendar demand shifts, rather than fixed multipliers.
- **Single-sensor granularity:** the system reasons at the zone level; it cannot yet localize a leak to a specific pipe segment or meter within a zone.
- **Synthetic data only:** the prototype runs on generated demo data. A production version would ingest live meter telemetry (e.g. via MQTT/IoT gateway) and would need to handle missing readings, clock drift, and sensor faults.
- **No persistence:** alerts and readings live in memory and reset on refresh/restart; a real system would log history to a database for trend analysis and audit trails.
- **No notification layer:** alerts are dashboard-only today; the next step would be email/SMS/webhook alerts to operations staff for High severity events.

## Folder Structure
```
aquaguard/
├── app.py                 # Flask app + routes
├── data_generator.py      # Synthetic water meter data
├── rules.py               # Rule-based anomaly detection engine
├── test_rules.py          # Unit tests for the detection engine
├── templates/
│   └── dashboard.html     # Dashboard UI (incl. zone flow chart)
├── static/
│   └── style.css          # Dark theme styling
├── requirements.txt
└── README.md
```
