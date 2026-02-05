# database.py
import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS motor_data (
    time TEXT,
    U1 REAL, U2 REAL, U3 REAL,
    I1 REAL, I2 REAL, I3 REAL,
    fault TEXT
)
""")
conn.commit()


def save_data(data, fault):
    cursor.execute(
        "INSERT INTO motor_data VALUES (?,?,?,?,?,?,?,?)",
        (
            data.timestamp,
            data.U1, data.U2, data.U3,
            data.I1, data.I2, data.I3,
            ",".join(fault)
        )
    )
    conn.commit()


def get_latest():
    cursor.execute("""
        SELECT * FROM motor_data
        ORDER BY time DESC
        LIMIT 1
    """)
    return cursor.fetchone()


def get_history(limit=100):
    cursor.execute("""
        SELECT * FROM motor_data
        ORDER BY time DESC
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()
