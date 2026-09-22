#!/bin/bash
# Force MQTT traffic through nfqueue for Python-based containment
iptables -I FORWARD -p tcp --dport 1883 -j NFQUEUE --queue-num 1
iptables -I FORWARD -p tcp --sport 1883 -j NFQUEUE --queue-num 1

iptables -t nat -A PREROUTING -p tcp --dport 1883 -j DNAT --to-destination $(getent hosts iot_broker | awk '{print $1}'):1883
iptables -t nat -A POSTROUTING -p tcp -d $(getent hosts iot_broker | awk '{print $1}') --dport 1883 -j MASQUERADE

# Note: Suricata configuration and Isolation Forest ML scripts will run here
echo "Edge Sensor configured for packet interception."

# Create logs directory if missing
mkdir -p /edge_sensor/logs

# Start Suricata in NFQUEUE mode, in the background
rm -f /var/run/suricata.pid
suricata -c /edge_sensor/suricata.yaml -q 1 -D

echo "Suricata started in NFQUEUE mode on queue 1."

# Start the Python ML detector in the background
# wait until python script is available before running
if [ -f /edge_sensor/detector/main.py ]; then
    cd /edge_sensor && python3 -m detector.main &
    echo "Python ML detector started."
else
    echo "Python ML detector not found yet, skipping..."
fi
