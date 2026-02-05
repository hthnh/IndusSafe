# simulator.py
import requests
import random
from datetime import datetime
import time

URL = "http://127.0.0.1:8000/api/data"

while True:
    payload = {
        "U1": random.uniform(210, 230),
        "U2": random.uniform(210, 230),
        "U3": random.uniform(0, 230),   # giả lập mất pha
        "I1": random.uniform(3, 6),
        "I2": random.uniform(3, 6),
        "I3": random.uniform(3, 6),
        "timestamp": datetime.now().isoformat()
    }

    r = requests.post(URL, json=payload)
    print(r.json())
    time.sleep(2)
