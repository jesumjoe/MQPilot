# FYP-V6-Simulator Analysis Report

## 1. Executive Summary

The **FYP-V6-Simulator** is a comprehensive IoT security simulator project designed to model an Internet of Things (IoT) environment undergoing real-time anomaly detection and incident response. The simulator comprises an edge sensor environment, an MQTT broker, simulated baseline traffic, a mock attacker machine, and a cloud-tier monitoring system that includes a Python Flask backend and a modern React (Vite) frontend.

The project demonstrates a security lifecycle where IoT devices transition through states (Normal -> Observed -> Suspicious -> Contained -> Critical) based on anomaly scores, packet rates, and trust levels.

## 2. System Architecture & Docker Compose Setup

The entire simulation is containerized and orchestrated via `docker-compose.yml`. The system operates on a custom bridge network called `iot_lan`.

The services included are:
- **`edge_sensor`**: Simulates the edge of the network. It requires elevated network capabilities (`NET_ADMIN`, `NET_RAW`) to manipulate iptables rules, intercepting MQTT traffic (Port 1883) and passing it to an NFQUEUE for packet inspection (intended for tools like Suricata or Python-based ML scripts like Isolation Forest).
- **`iot_broker`**: Runs an Eclipse Mosquitto instance on Port 1883. It acts as the central messaging hub for the simulated IoT devices.
- **`traffic_gen`**: A Python-based service that runs `generate_baseline.py`, generating continuous, baseline MQTT traffic on typical IoT topics (`sensor/temperature`, `sensor/humidity`, `device/status`) over a simulated 48-hour period.
- **`cloud_tier`**: A Python 3.11 container running a Flask API on port 5000. It simulates backend metric generation, state machine transitions, and serves as the data provider for the frontend dashboard.
- **`attacker_kali`**: A Kali Linux container equipped with network attack tools like `hydra` and `mosquitto-clients`. It sits on the network waiting for manual exploitation commands, simulating brute-force and payload injection attacks.

## 3. Component Analysis

### 3.1 Cloud Tier API (`cloud_tier/api/app.py`)
The Flask backend acts as the central intelligence and state manager for the simulated environment. 
- **Device Registry**: Hardcodes five simulated devices (Temperature Sensor, Humidity Sensor, Door Sensor, IP Camera, Smart Plug), each with an IP and an MQTT topic.
- **State Machine Engine**: Controls a 70-second continuous cyclic state progression for each device (`Normal` [20s] -> `Observed` [15s] -> `Suspicious` [15s] -> `Contained` [10s] -> `Critical` [10s]). The cycle visually simulates a security breach progression. Device states are stagger-started so the dashboard initially shows varied states.
- **Metrics Simulation**: Calculates dynamic metrics per state:
  - `packet_rate`: Spikes dramatically during `Suspicious` (184) and `Critical` (312), while dropping during `Contained` (6) to reflect quarantine rules.
  - `anomaly_score`: Escalates from 0.05 in `Normal` to 0.97 in `Critical`.
  - `trust_score`: Reversely scales from 100 to 2 as the threat escalates.
- **Alert Generation**: Triggers pre-defined alert messages depending on the current state. For example, `Suspicious` triggers Suricata and Isolation Forest warnings, while `Contained` logs NFQUEUE quarantine actions.
- **Endpoints**: Exposes `/api/devices` to fetch the real-time device states, and `/api/alerts` to fetch the chronological alert log.

### 3.2 Cloud Tier Frontend (`cloud_tier/frontend/`)
Built with React 19 and Vite, the frontend serves as a real-time Security Information and Event Management (SIEM) style dashboard.
- **Tech Stack**: React, Vite, CSS (custom styling with heavy animations and variables), no heavy component libraries ensuring a lightweight footprint.
- **Architecture**: 
  - Uses `useEffect` and `setInterval` to continuously poll the Flask `/api` every 5 seconds.
  - Maintains state arrays for `devices` and `alerts`, and uses a `useRef` to maintain rolling historical packet data to draw Sparkline graphs.
- **Key Components**:
  - `StatsBar`: Generates top-level visual pills counting the number of devices in each specific security state.
  - `DeviceGrid` & `DeviceCard`: The central visual element. It uses SVGs to draw custom `TrustGauge` components and `Sparkline` charts. Color-coding reflects the state (e.g., Green for Normal, Red for Critical).
  - `StateMachineDiagram`: A highly sophisticated raw SVG component that maps out the security state pipeline. It dynamically draws glowing rings and device avatars under the specific node representing their current state.
  - `AlertFeed`: Displays chronological SIEM alerts color-coded by severity (LOW, MEDIUM, HIGH, CRITICAL).

### 3.3 Edge Sensor (`edge_sensor/`)
Contains `setup_edge.sh` which injects `iptables` rules:
```bash
iptables -I FORWARD -p tcp --dport 1883 -j NFQUEUE --queue-num 1
iptables -I FORWARD -p tcp --sport 1883 -j NFQUEUE --queue-num 1
```
This forces all MQTT traffic (port 1883) into NFQUEUE queue 1. This implies that the simulator is designed to be paired with a packet inspector (e.g., Python `NetfilterQueue`) which evaluates the traffic against a Machine Learning model (like Isolation Forest) or an IDS (Suricata), dropping malicious packets.

### 3.4 Traffic Generator (`traffic_gen/generate_baseline.py`)
Uses the `paho-mqtt` library to connect to the `iot_broker` and continually publish randomized payloads (`value: 20-80`) to the broker on a loop with a random sleep timer (0.5 - 2.0s). This provides the baseline network noise necessary for the anomaly detection logic to have a benchmark to analyze.

## 4. Key Security Logic & State Transitions

The simulator perfectly models a 5-step incident response framework:
1. **Normal**: Trust Score (85-100). Low packet rate, minimal anomaly score.
2. **Observed**: Trust Score (60-84). Traffic rate quadruples; system begins logging unusual frequency.
3. **Suspicious**: Trust Score (35-59). Traffic spikes heavily. Anomaly scores breach 0.70. IDS logic flags brute-force attempts or malicious payload injections.
4. **Contained**: Trust Score (15-34). Traffic drops significantly as `IPTables` DROP rules and NFQUEUE quarantine device IPs.
5. **Critical**: Trust Score (2-14). Simulates a scenario where containment failed or a C2 beacon is established, leading to maximum anomaly scores.

## 5. Summary & Potential Improvements

The **FYP-V6-Simulator** is an excellent demonstrative tool for an IoT cybersecurity thesis or project. It efficiently mocks a complex IDS/IPS environment using standard containerization.

**Potential Extensions:**
1. **Actual Machine Learning Integration**: The cloud tier currently simulates the anomaly scores via hardcoded logic arrays. A real `Isolation Forest` model could be integrated into the edge sensor script to act upon the NFQUEUE packets.
2. **WebSockets**: The React frontend currently relies on HTTP Polling (every 5 seconds). Transitioning to `Socket.IO` or raw WebSockets would drastically reduce network overhead and provide instant UI updates.
3. **Kali Automation**: The Kali container is currently idle (`tail -f /dev/null`). Bash scripts could be introduced to automatically trigger `hydra` dictionary attacks periodically to generate genuine malicious traffic.
