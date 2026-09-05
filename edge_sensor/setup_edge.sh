#!/bin/bash
# Force MQTT traffic through nfqueue for Python-based containment
iptables -I FORWARD -p tcp --dport 1883 -j NFQUEUE --queue-num 1
iptables -I FORWARD -p tcp --sport 1883 -j NFQUEUE --queue-num 1

# Note: Suricata configuration and Isolation Forest ML scripts will run here
echo "Edge Sensor configured for packet interception."
