# main.py
from fastapi import FastAPI
from models import MotorData
from detector import detect_fault
from database import save_data, get_latest, get_history

app = FastAPI()


@app.post("/api/data")
def receive_data(data: MotorData):
    fault = detect_fault(data)
    save_data(data, fault)
    return {
        "status": "ok",
        "fault": fault
    }


@app.get("/api/latest")
def api_latest():
    row = get_latest()
    if not row:
        return {"status": "empty"}

    return {
        "time": row[0],
        "U": [row[1], row[2], row[3]],
        "I": [row[4], row[5], row[6]],
        "fault": row[7].split(",") if row[7] else []
    }


@app.get("/api/history")
def api_history(limit: int = 100):
    rows = get_history(limit)
    data = []

    for r in rows:
        data.append({
            "time": r[0],
            "U": [r[1], r[2], r[3]],
            "I": [r[4], r[5], r[6]],
            "fault": r[7].split(",") if r[7] else []
        })

    return data
