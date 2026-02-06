import json, time, random
from datetime import datetime
import paho.mqtt.client as mqtt

DEVICE_ID = "motor_01"
client = mqtt.Client()
client.connect("localhost", 1883, 60)

def on_message(c, u, msg):
    print("CMD:", msg.payload.decode())

client.subscribe(f"indussafe/cmd/{DEVICE_ID}")
client.on_message = on_message
client.loop_start()

while True:
    payload = {
        "U": [
            random.uniform(210, 230),
            random.uniform(210, 230),
            random.choice([0, random.uniform(210, 230)])
        ],
        "I": [
            random.uniform(3, 6),
            random.uniform(3, 6),
            random.uniform(3, 6)
        ],
        "ts": datetime.now().isoformat()
    }

    client.publish(
        f"indussafe/data/{DEVICE_ID}",
        json.dumps(payload)
    )

    time.sleep(2)
