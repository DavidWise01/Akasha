import os, sqlite3, json, time, hmac, hashlib, secrets
from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

DATA_DIR="/data"; SECRET_FILE=os.environ.get("SECRET_FILE",f"{DATA_DIR}/secret.key")
DB_FILE=f"{DATA_DIR}/witness.db"; MQTT_HOST=os.environ.get("MQTT_HOST","mqtt"); MQTT_PORT=int(os.environ.get("MQTT_PORT",1883))
os.makedirs(DATA_DIR,exist_ok=True)
if not os.path.exists(SECRET_FILE):
    open(SECRET_FILE,"w").write(secrets.token_hex(32))
SECRET=open(SECRET_FILE).read().strip().encode()
conn=sqlite3.connect(DB_FILE,check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS witness (id INTEGER PRIMARY KEY,ts REAL,topic TEXT,payload TEXT,hash TEXT,sig TEXT)"); conn.commit()
mqttc=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2); mqttc.connect(MQTT_HOST,MQTT_PORT,60); mqttc.loop_start()
app=Flask(__name__)
def sign(m): return hmac.new(SECRET,m.encode(),hashlib.sha256).hexdigest()

@app.post("/publish")
def pub():
    d=request.get_json(force=True); topic=d.get("topic","pocket/default"); payload=json.dumps(d.get("payload",{}))
    ts=time.time(); h=hashlib.sha256(payload.encode()).hexdigest(); sig=sign(f"{ts}|{topic}|{h}")
    mqttc.publish(topic,payload,qos=1)
    conn.execute("INSERT INTO witness(ts,topic,payload,hash,sig)VALUES(?,?,?,?,?)",(ts,topic,payload,h,sig)); conn.commit()
    return jsonify(ts=ts,topic=topic,hash=h,sig=sig,witness="recorded")

@app.get("/witness")
def wit(): return jsonify([dict(zip(["ts","topic","hash","sig"],r)) for r in conn.execute("SELECT ts,topic,hash,sig FROM witness ORDER BY id DESC LIMIT 100")])

@app.get("/health")
def health(): return {"status":"pocket universe alive","double_helix":"data + attribution"}

if __name__=="__main__": app.run(host="0.0.0.0",port=8080)
