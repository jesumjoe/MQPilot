import time
import random
from flask import Flask, jsonify

app = Flask(__name__)

# ── Device Registry ────────────────────────────────────────────────────────────
DEVICES = [
    {"id": "dev-001", "name": "Temperature Sensor", "ip": "192.168.1.101", "topic": "sensor/temperature"},
    {"id": "dev-002", "name": "Humidity Sensor",    "ip": "192.168.1.102", "topic": "sensor/humidity"},
    {"id": "dev-003", "name": "Door Sensor",         "ip": "192.168.1.103", "topic": "device/status"},
    {"id": "dev-004", "name": "IP Camera",           "ip": "192.168.1.104", "topic": "device/camera"},
    {"id": "dev-005", "name": "Smart Plug",          "ip": "192.168.1.105", "topic": "device/plug"},
]

# ── State Machine ──────────────────────────────────────────────────────────────
# Normal(20s) -> Observed(15s) -> Suspicious(15s) -> Contained(10s) -> Critical(10s) = 70s cycle
STATES          = ["Normal", "Observed", "Suspicious", "Contained", "Critical"]
STATE_DURATIONS = [20, 15, 15, 10, 10]
TOTAL_CYCLE     = sum(STATE_DURATIONS)  # 70 seconds

# Device offsets spread across all 5 state zones so every state is visible at startup:
# Normal:0-19, Observed:20-34, Suspicious:35-49, Contained:50-59, Critical:60-69
OFFSETS = [2, 25, 40, 55, 63]

# ── Trust Score Ranges ─────────────────────────────────────────────────────────
TRUST_RANGES = {
    "Normal":     (85, 100),
    "Observed":   (60, 84),
    "Suspicious": (35, 59),
    "Contained":  (15, 34),
    "Critical":   (2,  14),
}

# ── Baseline Metrics per State ─────────────────────────────────────────────────
METRICS_BASE = {
    "Normal":     {"packet_rate": 12,  "anomaly_score": 0.05},
    "Observed":   {"packet_rate": 48,  "anomaly_score": 0.38},
    "Suspicious": {"packet_rate": 184, "anomaly_score": 0.73},
    "Contained":  {"packet_rate": 6,   "anomaly_score": 0.91},
    "Critical":   {"packet_rate": 312, "anomaly_score": 0.97},
}

# ── Alert Templates (correlated to state transitions) ──────────────────────────
ALERT_TEMPLATES = {
    "Observed": [
        "Anomalous packet burst detected on {topic} from {ip}",
        "Unusual MQTT connection frequency from {ip} -- monitoring escalated",
    ],
    "Suspicious": [
        "[SIMULATED] Brute-Force attempt on {ip}:1883",
        "[SIMULATED] MQTT payload injection attempt on topic {topic} from {ip}",
        "[SIMULATED] Anomaly score 0.73 flagged for {name}",
    ],
    "Contained": [
        "[SIMULATED] Device {name} quarantined -- blocking {ip}",
        "[SIMULATED] DROP rule applied: {ip} port 1883",
        "[SIMULATED] HIGH anomaly score (0.91) sustained -- {name}",
    ],
    "Critical": [
        "[SIMULATED] C2 beacon pattern detected from {ip} on {topic}",
        "[SIMULATED] Data exfiltration volume spike -- {name} ({topic})",
        "[SIMULATED] Device {name} fully compromised -- manual intervention required",
    ],
}

SEVERITIES = {
    "Observed":   "LOW",
    "Suspicious": "MEDIUM",
    "Contained":  "HIGH",
    "Critical":   "CRITICAL",
}

# ── In-Memory Alert Store ───────────────────────────────────────────────────────
alert_log     = []
prev_states   = {}
_alert_id_ctr = [0]


def _push_alert(device, state):
    if state not in ALERT_TEMPLATES:
        return
    msg = random.choice(ALERT_TEMPLATES[state]).format(
        name=device["name"], ip=device["ip"], topic=device["topic"]
    )
    _alert_id_ctr[0] += 1
    alert_log.append({
        "id":          _alert_id_ctr[0],
        "device_id":   device["id"],
        "device_name": device["name"],
        "severity":    SEVERITIES.get(state, "INFO"),
        "state":       state,
        "message":     msg,
        "timestamp":   int(time.time()),
    })
    if len(alert_log) > 50:
        alert_log.pop(0)


def _get_state_and_progress(device_idx):
    t = (time.time() + OFFSETS[device_idx]) % TOTAL_CYCLE
    acc = 0
    for i, dur in enumerate(STATE_DURATIONS):
        if t < acc + dur:
            return STATES[i], (t - acc) / dur
        acc += dur
    return STATES[0], 0.0


def _trust_score(state, progress):
    lo, hi = TRUST_RANGES[state]
    return round(hi - (hi - lo) * progress)


def _metrics(state):
    base = METRICS_BASE[state]
    return {
        "packet_rate":   max(0, base["packet_rate"] + random.randint(-5, 5)),
        "anomaly_score": round(min(1.0, max(0.0, base["anomaly_score"] + random.uniform(-0.03, 0.03))), 3),
        "last_seen":     int(time.time()),
    }


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/api/devices")
def api_devices():
    result = []
    for i, device in enumerate(DEVICES):
        state, progress = _get_state_and_progress(i)
        if prev_states.get(device["id"]) != state:
            _push_alert(device, state)
            prev_states[device["id"]] = state
        result.append({
            **device,
            "state":       state,
            "trust_score": _trust_score(state, progress),
            "metrics":     _metrics(state),
        })
    return jsonify(result)


@app.route("/api/alerts")
def api_alerts():
    return jsonify(list(reversed(alert_log[-20:])))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
