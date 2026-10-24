import os, sqlite3, time, uuid
from flask import Flask, jsonify, request

app = Flask(__name__)
DB = os.environ.get("DB_PATH", "/data/appointments.db")
START = time.time()

def db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB, timeout=10)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("CREATE TABLE IF NOT EXISTS appts(id TEXT PRIMARY KEY, patient TEXT, doctor TEXT, slot TEXT, ts REAL)")
    return c

DOCTORS = [{"id": 1, "name": "Dr. Sharma", "dept": "Cardiology"},
           {"id": 2, "name": "Dr. Iyer", "dept": "Pediatrics"},
           {"id": 3, "name": "Dr. Khan", "dept": "Orthopedics"}]

@app.get("/health")
def health():
    return jsonify(status="UP", uptime_s=round(time.time() - START, 1))

@app.get("/api/doctors")
def doctors():
    return jsonify(DOCTORS)

@app.post("/api/appointments")
def book():
    d = request.get_json(force=True)
    aid = uuid.uuid4().hex[:8]
    c = db()
    c.execute("INSERT INTO appts VALUES (?,?,?,?,?)", (aid, d["patient"], d["doctor"], d["slot"], time.time()))
    c.commit(); c.close()
    return jsonify(id=aid, status="CONFIRMED"), 201

@app.get("/api/appointments")
def lst():
    c = db()
    rows = c.execute("SELECT id,patient,doctor,slot FROM appts ORDER BY ts DESC LIMIT 20").fetchall()
    c.close()
    return jsonify([dict(zip(("id", "patient", "doctor", "slot"), r)) for r in rows])
