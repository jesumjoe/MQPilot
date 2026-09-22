import paho.mqtt.client as mqtt
import time
import random
import sys

BROKER = "edge_sensor"
PORT = 1883
TOPICS = ["sensor/temperature", "sensor/humidity", "device/status"]

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to Simulated Broker with result code {reason_code}")

def run_attack(scenario):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    print(f"Running Attack Scenario: {scenario}")
    
    try:
        if scenario == "signature":
            # Scenario 6 - Signature trigger
            print("Sending malicious payload to trigger Suricata...")
            for _ in range(5):
                client.publish("device/status", "C2_BEACON")
                time.sleep(1)
                
        elif scenario == "rate":
            # Scenario 2 - Rate anomaly
            print("Flooding broker to trigger ML anomaly...")
            for _ in range(200):
                client.publish(random.choice(TOPICS), "value:99")
                time.sleep(0.01)
                
        elif scenario == "topic":
            # Scenario 3 - Topic anomaly
            print("Publishing to unusual topics...")
            for i in range(50):
                client.publish(f"unusual/topic_{i}", "test")
                time.sleep(0.1)
                
        elif scenario == "correlated":
            # Scenario 7 - Combined
            print("Flooding AND sending signatures...")
            for i in range(300):
                payload = "C2_BEACON" if i % 10 == 0 else "value:99"
                client.publish(random.choice(TOPICS), payload)
                time.sleep(0.01)
                
        else:
            print("Unknown scenario. Use: signature, rate, topic, correlated")

        time.sleep(2)
        print("Attack complete.")

    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_attack.py <scenario>")
        sys.exit(1)
    run_attack(sys.argv[1])
