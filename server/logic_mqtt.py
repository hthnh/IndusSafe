import json
from datetime import datetime
import paho.mqtt.client as mqtt
from detector import detect_fault
from database import save_data

BROKER = "localhost"
PORT = 1883
device_state = {}
def on_connect(client, userdata, flags, rc):
    print("MQTT connected:", rc)
    client.subscribe("indussafe/data/#")

def on_message(client, userdata, msg):
    device_id = msg.topic.split("/")[-1]
    payload = json.loads(msg.payload.decode())

    data = type("D", (), {})()
    data.U1, data.U2, data.U3 = payload["U"]
    data.I1, data.I2, data.I3 = payload["I"]
    data.timestamp = payload.get("ts", datetime.now().isoformat())

    faults = detect_fault(data)
    save_data(data, faults)

    is_critical = ("Mất pha" in faults) or ("Quá dòng" in faults)

    prev_state = device_state.get(device_id, "NORMAL")

    if is_critical and prev_state != "CRITICAL":
        client.publish(
            f"indussafe/cmd/{device_id}",
            json.dumps({"command": "CUT_POWER"})
        )
        device_state[device_id] = "CRITICAL"

    elif not is_critical:
        device_state[device_id] = "NORMAL"


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
