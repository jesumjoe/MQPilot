import paho.mqtt.client as mqtt
import time
import random

BROKER = "iot_broker"
PORT = 1883
TOPICS = ["sensor/temperature", "sensor/humidity", "device/status"]

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to Simulated Broker with result code {reason_code}")
    for topic in TOPICS:
        client.subscribe(topic)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

print("Initiating 48-hour baseline traffic simulation...")
try:
    while True:
        topic = random.choice(TOPICS)
        payload = f"value:{random.randint(20, 80)}"
        client.publish(topic, payload)
        time.sleep(random.uniform(0.5, 2.0)) # Tune traffic flow patterns
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
