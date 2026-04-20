import os, sqlite3, json, time, hmac, hashlib, secrets
from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

DATA_DIR = "/data"
SECRET_FILE = os.environ.get("SECRET_FILE", f"{DATA_DIR}/secret.key")
DB_FILE = f"{DATA_DIR}/witness.db"
MQTT_HOST = os.environ.get("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))

os.makedirs(DATA_DIR, exist_ok=True)

# generate secret on first run
if not os.path.exists(SECRET_FILE):
    with open(SECRET_FILE, "w") as f:
        f.write(secrets.token_hex(32))
with open(SECRET_FILE) as f:
    SECRET = f.read().strip().encode()

# init db
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
conn.execute("""CREATE TABLE IF NOT EXISTS witness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL,
    topic TEXT,
    payload TEXT,
    hash TEXT,
    sig TEXT
)""")
conn.commit()

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
mqtt_client.loop_start()

app = Flask(__name__)

def sign(msg):
    return hmac.new(SECRET, msg.encode(), hashlib.sha256).hexdigest()

@app.post("/publish")
def publish():
    data = request.get_json(force=True)
    topic = data.get("topic", "pocket/default")
    payload = json.dumps(data.get("payload", {}))
    ts = time.time()
    msg_hash = hashlib.sha256(payload.encode()).hexdigest()
    to_sign = f"{ts}|{topic}|{msg_hash}"
    sig = sign(to_sign)

    # data strand: publish to MQTT
    mqtt_client.publish(topic, payload, qos=1)

    # attribution strand: write witness
    conn.execute("INSERT INTO witness (ts, topic, payload, hash, sig) VALUES (?,?,?,?,?)",
                 (ts, topic, payload, msg_hash, sig))
    conn.commit()

    return jsonify({"ts": ts, "topic": topic, "hash": msg_hash, "sig": sig, "witness": "recorded"})

@app.get("/witness")
def witness():
    rows = conn.execute("SELECT ts, topic, hash, sig FROM witness ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify([{"ts": r[0], "topic": r[1], "hash": r[2], "sig": r[3]} for r in rows])

@app.get("/health")
def health():
    return {"status": "pocket universe alive", "double_helix": "data + attribution"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
