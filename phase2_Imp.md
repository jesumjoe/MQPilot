# MQPilot — Objective 2 Master Implementation Prompt

You are the primary software engineer responsible for implementing **Objective 2** of the MQPilot project.

## PROJECT CONTEXT

Repository:

`jesumjoe/MQPilot`

Current project objective 1 has established an IoT/MQTT security test environment using Docker.

The current repository contains approximately:

```text
MQPilot/
├── docker-compose.yml
├── edge_sensor/
│   └── setup_edge.sh
├── iot_broker/
│   └── mosquitto.conf
└── traffic_gen/
    └── generate_baseline.py
```

Current architecture:

```text
edge_sensor
iot_broker
traffic_gen
cloud_tier
attacker_kali
        │
        └── Docker bridge network: iot_lan
```

The current MQTT broker is Mosquitto on TCP port `1883`.

The current broker configuration explicitly allows anonymous connections:

```conf
listener 1883 0.0.0.0
allow_anonymous true
```

Do **not** redesign authentication as part of this task. Authentication is outside Objective 2.

The existing edge sensor currently contains:

```bash
iptables -I FORWARD -p tcp --dport 1883 -j NFQUEUE --queue-num 1
iptables -I FORWARD -p tcp --sport 1883 -j NFQUEUE --queue-num 1
```

The current traffic generator uses Paho MQTT and generates baseline MQTT traffic against:

```python
BROKER = "iot_broker"
PORT = 1883
```

with topics:

```text
sensor/temperature
sensor/humidity
device/status
```

The existing traffic generator should be treated as the starting point for **normal/baseline behavior**.

---

# PRIMARY OBJECTIVE

Implement:

> **A multi-plane detection engine combining Suricata IPS for signature-based threats and an Isolation Forest ML model for behavioral anomalies.**

The final architecture must contain three logical layers:

```text
              MQTT / IoT TRAFFIC
                       │
                       ▼
                EDGE / NFQUEUE
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   SIGNATURE PLANE            BEHAVIORAL PLANE
      Suricata IPS             Feature Extraction
      Custom Rules             Isolation Forest
          │                         │
          └────────────┬────────────┘
                       ▼
                 DECISION PLANE
                  Fusion Engine
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
           ALERT               ACTION
```

The implementation must be an actual functioning pipeline.

Do not merely install Suricata and train an ML model independently.

The two detection planes must feed a common decision/fusion layer.

---

# NON-NEGOTIABLE REQUIREMENTS

1. **Preserve Objective 1 functionality.**
2. Do not unnecessarily rewrite the existing architecture.
3. Do not introduce unnecessary infrastructure such as Kafka, Kubernetes, Redis, Elasticsearch, etc.
4. Keep the implementation Docker-based and compatible with the current repository.
5. Prefer simple, interpretable, testable Python components.
6. The Isolation Forest must be trained primarily on **normal/baseline traffic**, not attack traffic.
7. Suricata must function in IPS mode through NFQUEUE.
8. Suricata alerts must be available as structured EVE JSON.
9. MQTT behavioral features must be extracted from traffic telemetry.
10. The ML detector must operate on aggregated behavioral windows rather than arbitrary raw packets.
11. Suricata and ML outputs must be normalized into a common security-event format.
12. The fusion engine must distinguish:

* normal traffic
* signature-only detection
* behavioral-only anomaly
* correlated detection

13. The system must be testable using repeatable traffic scenarios.
14. Do not claim success unless the system has actually been executed and verified.

---

# PHASE 0 — REPOSITORY AUDIT

Before modifying files, inspect the entire repository.

Determine:

* current Docker architecture
* current container networking
* how the edge sensor is initialized
* whether Suricata is already installed
* whether the installed Suricata build supports NFQUEUE
* current iptables behavior
* MQTT connectivity
* current Mosquitto configuration
* current traffic-generator behavior
* available Python version
* available filesystem locations
* current logging behavior

Run appropriate commands/tests to establish a baseline.

Do not destroy or replace Objective 1 unnecessarily.

Document the baseline findings.

---

# PHASE 1 — SURICATA IPS PLANE

Implement the signature-based detection plane.

## 1. Suricata installation

Ensure the `edge_sensor` container has a working Suricata installation.

Verify:

```bash
suricata --build-info
suricata --version
```

Verify NFQUEUE support.

If installation method must change, modify Docker configuration cleanly rather than relying on manual setup that disappears after container recreation.

---

## 2. Suricata configuration

Create a repository-managed Suricata configuration.

Suggested location:

```text
edge_sensor/suricata.yaml
```

Do not blindly copy a configuration intended for another Suricata version.

Generate/use configuration compatible with the actual version installed in the container.

Configure:

* NFQUEUE IPS mode
* EVE JSON logging
* alert logging
* MQTT application-layer logging where supported
* appropriate network variables
* appropriate interface/network configuration
* rule path
* log directory
* safe defaults for the project

EVE JSON should be the primary machine-readable event interface.

---

# 3. NFQUEUE integration

The expected packet flow is:

```text
MQTT traffic
    ↓
iptables
    ↓
NFQUEUE queue 1
    ↓
Suricata IPS
    ↓
ACCEPT / DROP
```

Use queue `1` unless repository constraints require another queue.

Ensure Suricata is actually attached to the queue.

The implementation must not merely create iptables rules without a Suricata process consuming the queue.

Verify the full path experimentally.

---

# 4. Custom MQTT Suricata rules

Create a dedicated local rule file, for example:

```text
edge_sensor/rules/mqpilot.rules
```

The rules should be:

* MQTT-aware where possible
* understandable
* documented
* relevant to the project's threat model
* limited to useful detection cases

Target approximately **5–10 meaningful rules**, not dozens of artificial signatures.

Possible categories:

### Protocol abuse

Examples:

* suspicious MQTT protocol characteristics
* malformed/unusual control behavior

### Suspicious MQTT operations

Examples:

* suspicious topic activity
* suspicious control messages
* abnormal MQTT connection properties

### Known malicious indicators

Use harmless, controlled test signatures specifically for the project.

### Payload-based signatures

Create safe, deterministic signatures that can be triggered by the test traffic generator.

Do not rely exclusively on generic TCP signatures when MQTT-specific inspection is available.

Every custom rule must include a comment explaining:

* what it detects
* why it exists
* how it can be tested

At least one rule must be configured to produce an IPS `drop` action in a controlled test.

Do not configure legitimate baseline traffic to be dropped.

---

# PHASE 2 — EVE JSON TELEMETRY PIPELINE

Use Suricata EVE JSON as the telemetry interface wherever practical.

The system should be able to distinguish at minimum:

```text
event_type = alert
```

and relevant MQTT telemetry events.

Inspect the actual JSON generated by the installed Suricata version.

Do not invent field names.

Create a parser that tolerates:

* unrelated EVE events
* malformed JSON lines
* missing optional fields
* unexpected event types

Malformed individual records must not crash the whole detector.

---

# PHASE 3 — BEHAVIORAL FEATURE EXTRACTION

Create a Python feature-extraction pipeline.

Suggested location:

```text
edge_sensor/detector/feature_extractor.py
```

The detector must operate on **time-windowed behavioral observations**.

Default initial window:

```text
10 seconds
```

Make the window configurable.

For each window, generate an interpretable feature vector.

Start with approximately 12–20 features.

Recommended features:

## Traffic volume

```text
packet_count
byte_count
packets_per_second
bytes_per_second
```

## MQTT activity

```text
publish_count
subscribe_count
unsubscribe_count
connect_count
disconnect_count
```

## MQTT behavior

```text
unique_topics
average_payload_size
maximum_payload_size
qos_0_ratio
qos_1_ratio
qos_2_ratio
retain_ratio
duplicate_ratio
```

## Temporal behavior

```text
mean_inter_arrival_time
std_inter_arrival_time
```

## Connection behavior

Where the telemetry supports it:

```text
unique_source_count
unique_destination_count
connection_rate
```

Do not blindly implement a field if it is unavailable from the actual telemetry source.

Gracefully handle unavailable features.

---

# PHASE 4 — FEATURE DATASET

Create a clearly defined dataset format.

Suggested locations:

```text
edge_sensor/data/baseline/
edge_sensor/data/features/
```

Possible schema:

```text
timestamp
window_start
window_end
src_ip
dst_ip
packet_count
byte_count
packets_per_second
bytes_per_second
publish_count
subscribe_count
unsubscribe_count
connect_count
disconnect_count
unique_topics
average_payload_size
maximum_payload_size
qos_0_ratio
qos_1_ratio
qos_2_ratio
retain_ratio
duplicate_ratio
mean_inter_arrival_time
std_inter_arrival_time
```

Keep metadata separate from model features when appropriate.

Create a single authoritative feature-schema definition so training and inference cannot accidentally use different feature ordering.

---

# PHASE 5 — BASELINE COLLECTION

Use the existing `traffic_gen/generate_baseline.py` as the basis for normal behavior.

Do not contaminate the baseline dataset with attack traffic.

Create a repeatable baseline-collection mechanism.

The baseline pipeline should be:

```text
normal MQTT traffic
        ↓
Suricata telemetry
        ↓
feature extraction
        ↓
baseline feature dataset
```

Before training:

1. inspect the dataset
2. verify rows contain valid features
3. verify there are no accidental attack scenarios
4. verify the expected feature distributions
5. verify missing-value handling
6. verify that the model feature order is deterministic

---

# PHASE 6 — ISOLATION FOREST MODEL

Implement a training script.

Suggested location:

```text
edge_sensor/detector/train_model.py
```

Use `sklearn.ensemble.IsolationForest`.

Model requirements:

* unsupervised training
* baseline-only training by default
* deterministic random seed
* configurable `n_estimators`
* configurable `contamination`
* persisted model
* persisted feature schema
* reproducible preprocessing

Suggested artifact:

```text
edge_sensor/models/isolation_forest.joblib
```

Also persist the exact feature ordering and any preprocessing metadata.

Do not use attack labels as training targets.

The conceptual training flow is:

```text
baseline feature vectors
        ↓
preprocessing
        ↓
Isolation Forest.fit()
        ↓
persist model
```

---

# PHASE 7 — ANOMALY SCORING

Create a runtime inference component.

Suggested location:

```text
edge_sensor/detector/ml_detector.py
```

For every behavioral window:

```text
feature vector
      ↓
Isolation Forest
      ↓
anomaly score
      ↓
threshold decision
```

Return at minimum:

```json
{
  "timestamp": "...",
  "source": "...",
  "feature_window": "...",
  "anomaly_score": -0.12,
  "is_anomaly": true
}
```

Do not hardcode a random anomaly threshold.

Make the threshold configurable and document how it was selected.

Prefer a defensible calibration method based on baseline data.

For example, investigate the baseline score distribution and derive an initial threshold from it.

Document the tradeoff between:

* false positives
* sensitivity

The detector must expose the raw anomaly score in addition to the boolean decision.

---

# PHASE 8 — REAL-TIME ML DETECTOR

Implement streaming or near-real-time inference.

The expected pipeline is:

```text
EVE JSON
   ↓
MQTT event parser
   ↓
10-second rolling/window aggregation
   ↓
feature vector
   ↓
Isolation Forest
   ↓
ML detection event
```

The ML detector must continue running as a long-lived process.

It must not require retraining every time the detector starts.

It should load the persisted model artifact.

If the model is missing, fail clearly with an actionable error rather than silently pretending ML detection is active.

---

# PHASE 9 — FUSION / DECISION ENGINE

Create:

```text
edge_sensor/detector/fusion_engine.py
```

The fusion engine consumes:

```text
Suricata alerts
+
ML anomaly events
```

and generates unified security events.

Use a simple, explainable decision matrix.

## Case 1 — Normal

```text
Suricata: no alert
ML: no anomaly

=> NORMAL
```

## Case 2 — Signature-only

```text
Suricata: alert
ML: no anomaly

=> SIGNATURE_THREAT
```

## Case 3 — Behavioral-only

```text
Suricata: no alert
ML: anomaly

=> BEHAVIORAL_ANOMALY
```

## Case 4 — Correlated

```text
Suricata: alert
ML: anomaly

=> CORRELATED_THREAT
```

The system must preserve the individual evidence from both planes.

Do not throw away:

* Suricata signature ID
* Suricata severity
* rule name/signature
* source IP
* destination IP
* anomaly score
* feature-window information

---

# PHASE 10 — COMMON SECURITY EVENT SCHEMA

Define a single event format.

Suggested example:

```json
{
  "timestamp": "2026-09-21T18:00:00Z",
  "event_id": "...",
  "source_ip": "172.20.0.5",
  "destination_ip": "172.20.0.3",
  "destination_port": 1883,

  "signature": {
    "detected": true,
    "signature_id": 100001,
    "signature": "Example MQTT suspicious activity",
    "severity": 2
  },

  "behavioral": {
    "detected": true,
    "anomaly_score": -0.23,
    "window_seconds": 10,
    "feature_snapshot": {
      "packets_per_second": 85.3,
      "bytes_per_second": 12040,
      "publish_count": 420,
      "unique_topics": 17
    }
  },

  "classification": "CORRELATED_THREAT",
  "action": "ALERT"
}
```

Adapt the exact fields to the actual implementation.

The schema must remain stable and documented.

---

# PHASE 11 — RESPONSE / ACTION POLICY

Implement a conservative response policy.

For the initial implementation:

### Suricata signature detection

Known malicious traffic that matches an explicitly configured blocking rule may:

```text
DROP
```

### Isolation Forest anomaly

Do **not** automatically drop packets solely because the Isolation Forest reports an anomaly.

Instead:

```text
ML anomaly
    ↓
FLAG / ALERT
```

### Correlated detection

If both planes independently detect the same suspicious behavior:

```text
Suricata alert + ML anomaly
        ↓
CORRELATED_THREAT
        ↓
HIGH confidence
```

The initial implementation should prefer alerting over aggressive automated blocking unless a response is explicitly justified and tested.

Make response actions configurable.

---

# PHASE 12 — TEST TRAFFIC

Create a dedicated test traffic generator or extend the existing generator in a clean way.

Suggested:

```text
traffic_gen/generate_attack.py
```

All testing must be controlled and deterministic.

Create scenarios such as:

## Scenario 1 — Normal

Normal publish/subscription behavior.

Expected:

```text
Suricata = clean
ML = normal
Fusion = NORMAL
```

## Scenario 2 — Rate anomaly

Suddenly increase MQTT message frequency.

Expected:

```text
Suricata = potentially clean
ML = anomaly
Fusion = BEHAVIORAL_ANOMALY
```

## Scenario 3 — Topic anomaly

Generate many unusual topics within a short period.

Expected:

```text
ML = anomaly
```

## Scenario 4 — Payload/size anomaly

Generate unusually large or otherwise statistically unusual payloads.

Expected:

```text
ML = anomaly
```

## Scenario 5 — Connection burst

Rapidly create/disconnect MQTT connections.

Expected:

```text
ML = anomaly
```

## Scenario 6 — Signature trigger

Generate safe test traffic that deterministically matches one custom Suricata rule.

Expected:

```text
Suricata = alert
```

and, for a blocking rule:

```text
action = DROP
```

## Scenario 7 — Combined anomaly

Generate traffic that both:

* triggers a Suricata signature
* produces unusual behavioral statistics

Expected:

```text
Suricata = alert
ML = anomaly
Fusion = CORRELATED_THREAT
```

Do not use uncontrolled destructive attacks.

The purpose is detection-engine validation, not exploitation.

---

# PHASE 13 — AUTOMATED TESTING

Create tests.

Suggested structure:

```text
tests/
├── test_features.py
├── test_model.py
├── test_fusion.py
└── test_event_schema.py
```

Test at least:

### Feature extraction

* valid event parsing
* missing optional fields
* malformed event handling
* correct window aggregation
* correct feature calculations

### ML

* model loads successfully
* feature ordering is validated
* baseline observations are generally classified as normal
* synthetic abnormal observations can produce anomaly decisions

### Fusion

Test all four states:

```text
clean + clean
alert + clean
clean + anomaly
alert + anomaly
```

### Schema

Validate that generated security events contain required fields.

---

# PHASE 14 — INTEGRATION TEST

The agent must actually launch the Docker environment and prove the end-to-end path.

Required verification:

```text
traffic_gen
    ↓
MQTT broker
    ↓
iptables/NFQUEUE
    ↓
Suricata
    ↓
EVE JSON
    ↓
feature extraction
    ↓
Isolation Forest
    ↓
fusion
    ↓
security event
```

The agent must capture representative logs demonstrating the system works.

Do not merely run unit tests.

---

# PHASE 15 — EVALUATION METRICS

Create tooling that makes evaluation possible.

Measure at minimum:

## ML metrics

Where ground truth is available:

```text
Precision
Recall
F1-score
False Positive Rate
Detection Rate
```

For appropriate evaluation setups, also investigate:

```text
ROC-AUC
```

Do not fabricate metrics.

Only report values obtained from actual experiments.

---

# 16. MULTI-PLANE COMPARISON

Create an evaluation experiment comparing:

```text
Suricata only
Isolation Forest only
Suricata + Isolation Forest
```

The purpose is to demonstrate the reason for combining the planes.

Produce a table such as:

```text
Scenario                  Suricata   ML       Fusion
-----------------------------------------------------
Normal                    Clean      Normal   Normal
Known signature           Alert      Normal   Signature
Behavioral anomaly        Clean      Anomaly  Behavioral
Combined threat           Alert      Anomaly  Correlated
```

Then collect actual experiment results.

Do not invent the results during implementation.

---

# PHASE 17 — LOGGING

Implement structured logging.

At minimum, separate:

```text
Suricata logs
ML logs
Fusion/security-event logs
```

Use JSON where practical.

Avoid printing huge amounts of raw packet data continuously.

Include timestamps.

Include enough information to reproduce/debug detections.

---

# PHASE 18 — CONFIGURATION

Do not scatter magic values throughout Python files.

Create centralized configuration.

Possible configurable values:

```text
MQTT port
NFQUEUE number
ML window size
ML contamination
model path
feature dataset path
anomaly threshold
EVE JSON path
log path
```

Environment variables or a small configuration module are acceptable.

Do not hardcode absolute host-specific paths.

---

# PHASE 19 — DOCKER INTEGRATION

Modify:

```text
docker-compose.yml
```

only as necessary.

The final environment should allow:

```bash
docker compose up
```

to start the complete test environment.

The edge sensor must contain:

* Suricata
* Python detector
* required Python dependencies
* configuration
* rules
* model-loading capability

Avoid unnecessary new containers unless there is a compelling architectural reason.

Keep the project simple.

---

# PHASE 20 — REPRODUCIBILITY

The entire implementation must be reproducible from a fresh checkout.

A developer should be able to:

```text
clone repository
       ↓
build/start containers
       ↓
generate baseline
       ↓
train model
       ↓
start detector
       ↓
run test traffic
       ↓
observe detection events
```

Document this process.

No undocumented manual steps.

No dependency on files existing only on the developer's machine.

---

# PHASE 21 — DOCUMENTATION

Create or update:

```text
docs/objective2.md
```

Document:

## Architecture

Explain:

```text
NFQUEUE
Suricata IPS
EVE JSON
feature extractor
Isolation Forest
fusion engine
```

## Request/data flow

Show:

```text
MQTT traffic
    ↓
Suricata
    ↓
EVE telemetry
    ↓
feature extraction
    ↓
Isolation Forest
    ↓
fusion
    ↓
security decision
```

## Signature plane

Explain:

* Suricata role
* custom rules
* IPS behavior
* EVE alerts

## Behavioral plane

Explain:

* baseline collection
* features
* windowing
* Isolation Forest
* anomaly score
* threshold

## Fusion plane

Explain the four decision states.

## Training procedure

Explain exactly how the baseline is collected and how the model is trained.

## Testing

Document all attack/anomaly simulation scenarios.

## Limitations

Explicitly document:

* unsupervised ML does not identify the exact attack type by itself
* baseline quality affects model quality
* behavioral thresholds affect false positives
* model drift is possible
* Suricata and ML operate at different time scales

Do not hide limitations.

---

# IMPORTANT DESIGN PRINCIPLES

## Principle 1 — Objective 1 must remain functional

Do not destroy the existing:

```text
MQTT broker
traffic generator
Docker network
edge_sensor
attacker_kali
```

unless modification is required for Objective 2.

---

## Principle 2 — Suricata and ML are complementary

Do not make Isolation Forest pretend to perform signature classification.

Use:

```text
Suricata → known threat signatures
Isolation Forest → behavioral deviations
Fusion → combined security interpretation
```

---

## Principle 3 — Use interpretable features

Prefer:

```text
message rate
payload size
topic diversity
connection rate
timing
MQTT operation frequency
```

over arbitrary opaque packet features.

---

## Principle 4 — Preserve raw evidence

Every high-level detection must be traceable to:

```text
Suricata evidence
or
ML feature window
or
both
```

---

## Principle 5 — Avoid false claims

Never write:

> "The ML model detects ransomware."

unless there is actual experimental evidence supporting that statement.

The correct interpretation of the initial ML component is:

> "The Isolation Forest detects behavioral deviations from the learned baseline."

Attack-specific identification belongs to signatures, correlation, or a later classification component.

---

# TARGET REPOSITORY STRUCTURE

Aim for a structure broadly resembling:

```text
MQPilot/
│
├── docker-compose.yml
│
├── edge_sensor/
│   ├── setup_edge.sh
│   ├── suricata.yaml
│   │
│   ├── rules/
│   │   └── mqpilot.rules
│   │
│   ├── detector/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── feature_extractor.py
│   │   ├── train_model.py
│   │   ├── ml_detector.py
│   │   └── fusion_engine.py
│   │
│   ├── models/
│   │   └── isolation_forest.joblib
│   │
│   ├── data/
│   │   ├── baseline/
│   │   └── features/
│   │
│   └── logs/
│       ├── eve.json
│       ├── ml_detector.json
│       └── security_events.json
│
├── traffic_gen/
│   ├── generate_baseline.py
│   └── generate_attack.py
│
├── tests/
│   ├── test_features.py
│   ├── test_model.py
│   ├── test_fusion.py
│   └── test_event_schema.py
│
└── docs/
    └── objective2.md
```

This is a target, not a requirement to blindly create every file.

Use your engineering judgement based on the existing repository.

---

# IMPLEMENTATION ORDER

Follow this order:

```text
1. Audit repository
2. Verify Docker/MQTT baseline
3. Implement Suricata
4. Connect Suricata to NFQUEUE
5. Enable EVE JSON
6. Add/test custom rules
7. Verify signature detection
8. Build telemetry parser
9. Build feature extractor
10. Collect clean baseline
11. Train Isolation Forest
12. Validate model
13. Build real-time ML detector
14. Build fusion engine
15. Add deterministic test scenarios
16. Run end-to-end integration
17. Measure results
18. Harden implementation
19. Write documentation
20. Run final regression tests
```

Do not jump directly to the ML model before the Suricata telemetry pipeline works.

---

# DEFINITION OF DONE

Objective 2 is complete only when all of the following are true:

### Suricata

* Suricata successfully runs in the edge container.
* NFQUEUE integration works.
* MQTT traffic reaches Suricata.
* Custom rules load without errors.
* At least one known test signature produces an alert.
* At least one explicitly blocking signature demonstrates packet/flow dropping in a controlled test.
* EVE JSON is populated.

### Isolation Forest

* Baseline dataset is generated from normal traffic.
* Feature extraction works.
* Feature schema is deterministic.
* Isolation Forest trains successfully.
* Model artifact is persisted.
* Runtime detector loads the model.
* Anomaly scores are produced.
* At least one controlled abnormal behavior is detected.
* Baseline traffic does not produce an unacceptable flood of false positives in the test environment.

### Fusion

* Suricata-only event works.
* ML-only anomaly works.
* Correlated event works.
* Normal traffic is classified as normal.
* Unified security events contain evidence from the underlying detectors.

### Integration

The following complete flow must work:

```text
MQTT traffic
      ↓
NFQUEUE
      ↓
Suricata IPS
      ↓
EVE JSON
      ↓
Feature extraction
      ↓
Isolation Forest
      ↓
Fusion Engine
      ↓
Security Event
```

### Documentation

* Architecture documented.
* Setup documented.
* Training documented.
* Testing documented.
* Limitations documented.
* Actual observed results documented.

---

# FINAL ENGINEERING RULE

Work like a production engineer, not like a code generator.

Before each major change:

1. inspect the existing implementation
2. understand why it exists
3. make the smallest necessary change
4. run a relevant test
5. verify that Objective 1 still works
6. continue

Do not replace working components just because another implementation is easier.

Do not create placeholder code and mark the task complete.

Do not fabricate test results, metrics, logs, or successful detections.

When finished, provide a final engineering report containing:

```text
1. Files created
2. Files modified
3. Architecture implemented
4. Suricata configuration
5. ML pipeline
6. Feature schema
7. Fusion logic
8. Test scenarios
9. Actual test results
10. Known limitations
11. Commands to reproduce the complete system
12. Any remaining issues
```

The final implementation should make the statement below genuinely true:

> **MQPilot implements a multi-plane IoT/MQTT detection engine in which Suricata provides signature-based inline detection and enforcement, Isolation Forest identifies behavioral anomalies from baseline traffic, and a fusion layer correlates both detection planes into unified security events.**
