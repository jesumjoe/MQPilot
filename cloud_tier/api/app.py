import json
import time
import os
import threading
from flask import Flask, jsonify

app = Flask(__name__)

# Real devices from the Kaggle dataset
DEVICES = [
    {"id": "dev-001", "name": "Door Lock Sensor",    "ip": "192.168.0.176", "topic": "Door Lock"},
    {"id": "dev-002", "name": "Light Intensity",     "ip": "192.168.0.150", "topic": "Light Intensity"},
    {"id": "dev-003", "name": "Temperature Sensor",  "ip": "192.168.0.151", "topic": "Temperature"},
    {"id": "dev-004", "name": "Smoke Detector",      "ip": "192.168.0.180", "topic": "Smoke"},
    {"id": "dev-005", "name": "Fan Controller",      "ip": "192.168.0.178", "topic": "Fan"},
]

SECURITY_EVENTS_PATH = "/edge_sensor/logs/security_events.json"

# In-memory store updated by the real security events
device_states = {d["id"]: {
    "state": "Normal",
    "trust_score": 100,
    "metrics": {"packet_rate": 0, "anomaly_score": 0.0, "last_seen": int(time.time())}
} for d in DEVICES}

ip_to_dev_id = {d["ip"]: d["id"] for d in DEVICES}

alert_log = []
_alert_id_ctr = 0

def map_classification_to_state(classification):
    if classification == "NORMAL": return "Normal"
    if classification == "BEHAVIORAL_ANOMALY": return "Observed"
    if classification == "SIGNATURE_THREAT": return "Suspicious"
    if classification == "CORRELATED_THREAT": return "Critical"
    return "Normal"

def map_state_to_trust(state):
    mapping = {"Normal": 95, "Observed": 70, "Suspicious": 45, "Contained": 25, "Critical": 5}
    return mapping.get(state, 100)

def map_state_to_severity(state):
    mapping = {"Normal": "INFO", "Observed": "LOW", "Suspicious": "MEDIUM", "Contained": "HIGH", "Critical": "CRITICAL"}
    return mapping.get(state, "INFO")

def tail_events():
    global _alert_id_ctr
    print("Starting security events tail thread...")
    while not os.path.exists(SECURITY_EVENTS_PATH):
        time.sleep(2)
        
    with open(SECURITY_EVENTS_PATH, 'r') as f:
        # Seek to the end if we only want live events, but for demo we can read from start
        # f.seek(0, 2) 
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            
            try:
                evt = json.loads(line)
            except:
                continue
                
            src_ip = evt.get("source_ip")
            
            # Update device state based on IP
            dev_id = ip_to_dev_id.get(src_ip)
            if not dev_id and src_ip == "multiple":
                # Apply to all
                dev_ids = list(device_states.keys())
            elif dev_id:
                dev_ids = [dev_id]
            else:
                continue

            classification = evt.get("classification", "NORMAL")
            new_state = map_classification_to_state(classification)
            beh = evt.get("behavioral", {}) or {}
            
            # Extract metrics
            anomaly_score = beh.get("anomaly_score", 0.0)
            feat = beh.get("feature_snapshot", {})
            pkt_rate = feat.get("packets_per_second", 0)

            for d_id in dev_ids:
                device_states[d_id]["state"] = new_state
                device_states[d_id]["trust_score"] = map_state_to_trust(new_state)
                device_states[d_id]["metrics"]["anomaly_score"] = round(anomaly_score, 3)
                if pkt_rate:
                    device_states[d_id]["metrics"]["packet_rate"] = int(pkt_rate)
                device_states[d_id]["metrics"]["last_seen"] = int(time.time())

            # Generate alert if not Normal
            if new_state != "Normal":
                sig = evt.get("signature", {}) or {}
                sig_msg = sig.get("signature", "Unknown Signature")
                
                msg = f"Threat Detected: {classification}"
                if sig.get("detected"):
                    msg += f" | {sig_msg}"
                
                _alert_id_ctr += 1
                
                # find dev name
                dev_name = "Multiple Devices"
                if len(dev_ids) == 1:
                    dev_name = next(d["name"] for d in DEVICES if d["id"] == dev_ids[0])
                
                alert_log.append({
                    "id": _alert_id_ctr,
                    "device_id": dev_ids[0] if len(dev_ids) == 1 else "sys",
                    "device_name": dev_name,
                    "severity": map_state_to_severity(new_state),
                    "state": new_state,
                    "message": msg,
                    "timestamp": int(time.time()),
                })
                
                if len(alert_log) > 50:
                    alert_log.pop(0)

# Start background thread
threading.Thread(target=tail_events, daemon=True).start()

@app.route("/api/devices")
def api_devices():
    result = []
    for d in DEVICES:
        st = device_states[d["id"]]
        result.append({
            **d,
            "state": st["state"],
            "trust_score": st["trust_score"],
            "metrics": st["metrics"]
        })
    return jsonify(result)

@app.route("/api/alerts")
def api_alerts():
    return jsonify(list(reversed(alert_log[-20:])))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
