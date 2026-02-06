from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sqlite3
import paho.mqtt.client as mqtt
import json

app = FastAPI()

# ---------- DATABASE ----------
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# ---------- MQTT ----------
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()


@app.get("/api/latest")
def api_latest():
    cursor.execute("""
        SELECT * FROM motor_data
        ORDER BY time DESC LIMIT 1
    """)
    row = cursor.fetchone()

    if not row:
        return {"status": "NO_DATA"}

    faults = row[7].split(",") if row[7] else []

    if "Mất pha" in faults or "Quá dòng" in faults:
        state = "CRITICAL"
    elif len(faults) > 0:
        state = "WARNING"
    else:
        state = "NORMAL"

    return {
        "time": row[0],
        "U": [row[1], row[2], row[3]],
        "I": [row[4], row[5], row[6]],
        "fault": faults,
        "state": state
    }




@app.post("/api/reset/{device_id}")
def reset_device(device_id: str):
    mqtt_client.publish(
        f"indussafe/cmd/{device_id}",
        json.dumps({"command": "RESET"})
    )
    return {"status": "RESET_SENT"}




@app.post("/api/manual_cut/{device_id}")
def manual_cut(device_id: str):
    mqtt_client.publish(
        f"indussafe/cmd/{device_id}",
        json.dumps({"command": "CUT_POWER"})
    )
    return {"status": "SENT"}


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>IndusSafe Dashboard</title>
<style>
  body { font-family: Arial; background:#111; color:#eee; padding:20px; }
  .card { background:#222; padding:15px; margin:10px 0; border-radius:8px; }
  .ok { color:#0f0; }
  .warn { color:#ff0; }
  .crit { color:#f00; }
  button { padding:10px; font-size:16px; margin-right:10px; }
  canvas { background:#000; }
</style>
</head>

<body>

<h1>⚙️ IndusSafe – Motor 3 Pha (LAN Mode)</h1>

<div class="card">
  <h3>Điện áp (V)</h3>
  <div id="voltage">---</div>
</div>

<div class="card">
  <h3>Dòng điện (A)</h3>
  <div id="current">---</div>
</div>

<div class="card">
  <h3>Trạng thái</h3>
  <div id="status">---</div>
</div>

<div class="card">
  <button onclick="cutPower()">🛑 NGẮT TẢI</button>
  <button onclick="resetPower()">🔄 RESET</button>
</div>

<div class="card">
  <h3>Biểu đồ dòng điện (Realtime)</h3>
  <canvas id="chart" width="600" height="200"></canvas>
</div>

<script>
const DEVICE_ID = "motor_01";
const MAX_POINTS = 50;

let i1=[], i2=[], i3=[];

const canvas = document.getElementById("chart");
const ctx = canvas.getContext("2d");

function drawChart() {
  ctx.clearRect(0,0,canvas.width,canvas.height);

  const maxI = Math.max(...i1, ...i2, ...i3, 10);
  const scaleY = canvas.height / maxI;
  const stepX = canvas.width / MAX_POINTS;

  function drawLine(data, color) {
    ctx.strokeStyle = color;
    ctx.beginPath();
    data.forEach((v, idx) => {
      const x = idx * stepX;
      const y = canvas.height - v * scaleY;
      idx === 0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
    });
    ctx.stroke();
  }

  drawLine(i1, "red");
  drawLine(i2, "yellow");
  drawLine(i3, "cyan");
}

function update() {
  fetch("/api/latest")
    .then(r=>r.json())
    .then(d=>{
      if (d.status==="NO_DATA") return;

      document.getElementById("voltage").innerText =
        d.U.map(v=>v.toFixed(1)).join(" | ");

      document.getElementById("current").innerText =
        d.I.map(i=>i.toFixed(2)).join(" | ");

      let cls = d.state==="CRITICAL"?"crit":d.state==="WARNING"?"warn":"ok";
      document.getElementById("status").innerHTML =
        `<span class="${cls}">${d.state}</span>`;

      i1.push(d.I[0]); i2.push(d.I[1]); i3.push(d.I[2]);
      if (i1.length>MAX_POINTS) {
        i1.shift(); i2.shift(); i3.shift();
      }
      drawChart();
    });
}

function cutPower() {
  fetch(`/api/manual_cut/${DEVICE_ID}`, {method:"POST"});
}

function resetPower() {
  fetch(`/api/reset/${DEVICE_ID}`, {method:"POST"});
}

setInterval(update, 2000);
update();
</script>

</body>
</html>

"""
