
from flask import Flask, request, jsonify, render_template_string
import hashlib, json, time, secrets, os

app = Flask(__name__)
WITNESS_LOG = []
KEYS = {}
CORP_KEYS = []
MEDIA_VAULT = []  # user can add, core stays same
PATTERN = "5554443332221110111222333444555"
HB = "honeybadger"
J5 = "j5"
CORP_CAP = 10
INHERITANCE_RATE = 0.9
MAX_PAYLOAD = 131072

DATA_FILE = "/tmp/vault.json"
if os.path.exists(DATA_FILE):
    try: MEDIA_VAULT = json.load(open(DATA_FILE))
    except: pass

def save_vault():
    json.dump(MEDIA_VAULT, open(DATA_FILE,"w"))

def witness(t,d,parent=None,weight=1.0):
    raw = json.dumps(d, sort_keys=True)
    if len(raw.encode()) > MAX_PAYLOAD:
        d = {"hash_only": hashlib.sha256(raw.encode()).hexdigest(), "truncated": True}
        raw = json.dumps(d, sort_keys=True)
    s = {"ts":int(time.time()),"type":t,"data":d,"pattern":PATTERN,"parent":parent,"weight":round(weight*0.9,6),"corp_share":0.1,"hb":HB,"j5":J5,"hash":hashlib.sha256((PATTERN+raw).encode()).hexdigest()[:16]}
    WITNESS_LOG.append(s); return s

for i in range(89):
    k = "010-" + secrets.token_hex(4)
    KEYS[k] = {"gen":0,"type":"commons","weight":1.0}
    witness("genesis_commons",{"key":k})

MONOLITH_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>INTERNET RESTORE // MONOLITH</title>
<meta name="theme-color" content="#000000">
<style>
:root {
  --green: #00ff00;
  --yellow: #ffff00;
  --green-dim: #00aa00;
  --bg: #000;
}
* { box-sizing: border-box; }
html, body { height: 100%; }
body {
  margin: 0;
  background: #000;
  color: var(--green);
  font-family: "Courier New", Courier, "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 14px;
  line-height: 1.5;
  overflow-x: hidden;
  -webkit-font-smoothing: none;
  -moz-osx-font-smoothing: grayscale;
}
body::before {
  content: "";
  position: fixed;
  inset: 0;
  background: radial-gradient(ellipse at center, rgba(0,255,0,0.07) 0%, transparent 65%);
  pointer-events: none;
  z-index: 0;
}
.scanlines {
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    to bottom,
    rgba(0,255,0,0.08) 0px,
    rgba(0,255,0,0.08) 1px,
    transparent 2px,
    transparent 4px
  );
  opacity: 0.22;
  pointer-events: none;
  z-index: 100;
  mix-blend-mode: screen;
}
.crt-flicker {
  position: fixed;
  inset: 0;
  background: rgba(0,255,0,0.012);
  pointer-events: none;
  z-index: 101;
  animation: flicker 0.13s infinite steps(1);
}
@keyframes flicker { 0%,19%{opacity:.03}20%{opacity:.01}21%,39%{opacity:.03}40%{opacity:.02}60%{opacity:.04}80%{opacity:.01}100%{opacity:.03} }

.wrap {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 10px;
  max-width: 1440px;
  margin: 0 auto;
}

header {
  text-align: center;
  padding: 18px 0 14px;
  border-bottom: 1px solid rgba(0,255,0,0.25);
}
.header-title {
  font-size: clamp(20px, 3.2vw, 32px);
  font-weight: 700;
  letter-spacing: 0.14em;
  margin: 0;
  color: var(--green);
  text-shadow: 0 0 10px rgba(0,255,0,0.9), 0 0 24px rgba(0,255,0,0.5);
}
.cursor {
  display: inline-block;
  width: 0.6ch;
  height: 1.1em;
  background: var(--green);
  margin-left: 4px;
  transform: translateY(2px);
  animation: blink 1.1s steps(1,end) infinite;
  box-shadow: 0 0 12px var(--green);
}
@keyframes blink { 0%,50%{opacity:1} 51%,100%{opacity:0} }
.header-sub {
  margin-top: 8px;
  font-size: 11px;
  color: var(--green-dim);
  letter-spacing: 0.28em;
  text-transform: uppercase;
}

.ticker-wrap {
  border-top: 1px solid rgba(0,255,0,0.15);
  border-bottom: 1px solid rgba(0,255,0,0.15);
  background: rgba(0,255,0,0.025);
  overflow: hidden;
  margin-top: 8px;
  position: relative;
}
.ticker {
  display: flex;
  width: max-content;
  white-space: nowrap;
  will-change: transform;
  animation: scroll 50s linear infinite;
  padding: 6px 0;
}
.ticker:hover { animation-play-state: paused; }
.ticker-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 26px;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: var(--green);
  text-shadow: 0 0 6px rgba(0,255,0,0.65);
  border-right: 1px dotted rgba(0,255,0,0.18);
}
.ticker-item .name { color: var(--yellow); text-shadow: 0 0 6px rgba(255,255,0,0.5); }
.ticker-item .val { min-width: 6ch; text-align: right; }
.ticker-item .delta { color: var(--green); }
.arrow { color: var(--green); }
@keyframes scroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }

main {
  flex: 1;
  display: grid;
  grid-template-columns: 290px minmax(320px,1fr) 290px;
  gap: 22px;
  padding: 22px 0;
  align-items: start;
}
@media (max-width: 1100px) {
  main { grid-template-columns: 1fr; gap: 24px; }
  .monolith-wrap { order: 1; }
  .left { order: 2; }
  .right { order: 3; }
}

.panel {
  border: 1px solid rgba(0,255,0,0.35);
  background: rgba(0,0,0,0.82);
  box-shadow: inset 0 0 24px rgba(0,255,0,0.04), 0 0 0 1px #000;
  padding: 14px;
  position: relative;
}
.panel::before {
  content: "";
  position: absolute;
  inset: 0;
  margin: 3px;
  border: 1px solid rgba(0,255,0,0.1);
  pointer-events: none;
}
.panel-title {
  font-size: 12px;
  color: var(--yellow);
  letter-spacing: 0.18em;
  margin: 0 0 14px;
  text-transform: uppercase;
  text-shadow: 0 0 8px rgba(255,255,0,0.55);
}
.panel-list { display: flex; flex-direction: column; gap: 10px; }
.vault-item {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 9px 10px;
  border: 1px solid rgba(0,255,0,0.18);
  background: rgba(0,255,0,0.025);
  font-size: 12px;
  transition: background .2s;
}
.vault-item:hover { background: rgba(0,255,0,0.05); }
.vault-item .name { color: var(--green); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.btn-upload {
  font-family: inherit;
  font-size: 10px;
  background: transparent;
  color: var(--green);
  border: 1px solid var(--green);
  padding: 5px 10px;
  cursor: pointer;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  transition: all .15s;
  box-shadow: 0 0 10px rgba(0,255,0,0.18) inset;
}
.btn-upload:hover { background: var(--green); color: #000; box-shadow: 0 0 16px rgba(0,255,0,0.9); text-shadow: none; }
.btn-upload:active { transform: translateY(1px); }
.btn-upload:disabled { opacity: 0.7; }

.monolith-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 64vh;
}
.monolith {
  position: relative;
  width: min(360px, 78vw);
  height: min(70vh, 660px);
  background: #000;
  border: 1px solid rgba(0,255,0,0.55);
  box-shadow:
    0 0 0 2px #000,
    0 0 40px rgba(0,255,0,0.18),
    0 0 120px rgba(0,255,0,0.09),
    inset 0 0 50px rgba(0,255,0,0.06);
  overflow: hidden;
  isolation: isolate;
}
.monolith::before {
  content: "";
  position: absolute;
  inset: -20%;
  background: conic-gradient(from 0deg, transparent, rgba(0,255,0,0.12), transparent 30%);
  animation: spin 18s linear infinite;
  z-index: 0;
  opacity: 0.4;
}
@keyframes spin { to { transform: rotate(360deg);} }
.monolith::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, rgba(0,255,0,0.08) 50%, transparent 100%);
  transform: translateY(-100%);
  animation: sweep 3.5s linear infinite;
  mix-blend-mode: screen;
  pointer-events: none;
}
@keyframes sweep { 0%{transform:translateY(-100%)} 100%{transform:translateY(100%)} }
#monolith-canvas {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: block;
  background: #000;
  cursor: crosshair;
}
.monolith-label {
  position: absolute;
  bottom: 10px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 10px;
  letter-spacing: 0.32em;
  color: rgba(0,255,0,0.55);
  z-index: 2;
  text-shadow: 0 0 6px rgba(0,255,0,0.5);
  pointer-events: none;
}

.right .kv { font-size: 12px; line-height: 1.9; }
.kv-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 5px 0;
  border-bottom: 1px dotted rgba(0,255,0,0.14);
}
.kv-row span:first-child { color: var(--green-dim); text-transform: uppercase; letter-spacing: 0.06em; }
.kv-row span:last-child { color: var(--yellow); text-shadow: 0 0 6px rgba(255,255,0,0.45); }
.kv-row.active span:last-child { color: var(--green); text-shadow: 0 0 10px rgba(0,255,0,0.85); animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.7} }
.pattern {
  margin-top: 14px;
  padding: 10px 8px;
  border: 1px solid rgba(255,255,0,0.28);
  background: rgba(255,255,0,0.04);
  font-size: 11px;
  word-break: break-all;
  color: var(--yellow);
  text-align: center;
  letter-spacing: 0.12em;
  line-height: 1.6;
  text-shadow: 0 0 8px rgba(255,255,0,0.35);
}

.cap {
  border-top: 1px solid rgba(0,255,0,0.25);
  border-bottom: 1px solid rgba(0,255,0,0.25);
  background: linear-gradient(180deg, rgba(0,255,0,0.03), rgba(0,0,0,0));
  padding: 20px 14px 18px;
  text-align: center;
  margin-top: auto;
}
.cap-title {
  font-size: 13px;
  letter-spacing: 0.24em;
  color: var(--yellow);
  margin: 0 0 16px;
  text-transform: uppercase;
  text-shadow: 0 0 10px rgba(255,255,0,0.5);
}
.cap-buttons { display: flex; gap: 18px; justify-content: center; flex-wrap: wrap; }
.btn-cap {
  position: relative;
  display: inline-block;
  padding: 14px 32px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-decoration: none;
  text-transform: uppercase;
  background: #000;
  border: 2px solid;
  transition: all .18s ease;
  min-width: 210px;
  overflow: hidden;
}
.btn-cap::before {
  content: "";
  position: absolute;
  inset: 0;
  background: currentColor;
  opacity: 0;
  transition: opacity .18s;
}
.btn-cap:hover::before { opacity: 0.12; }
.btn-commons {
  color: var(--green);
  border-color: var(--green);
  box-shadow: 0 0 18px rgba(0,255,0,0.22), inset 0 0 12px rgba(0,255,0,0.08);
  text-shadow: 0 0 8px rgba(0,255,0,0.75);
}
.btn-commons:hover { background: var(--green); color: #000; box-shadow: 0 0 36px rgba(0,255,0,0.95); text-shadow: none; }
.btn-corp {
  color: var(--yellow);
  border-color: var(--yellow);
  box-shadow: 0 0 18px rgba(255,255,0,0.22), inset 0 0 12px rgba(255,255,0,0.08);
  text-shadow: 0 0 8px rgba(255,255,0,0.75);
}
.btn-corp:hover { background: var(--yellow); color: #000; box-shadow: 0 0 36px rgba(255,255,0,0.95); text-shadow: none; }
.cap-remain { margin-top: 12px; font-size: 11px; color: var(--green-dim); letter-spacing: 0.18em; }

footer {
  text-align: center;
  padding: 16px 0 8px;
  font-size: 11px;
  color: rgba(0,255,0,0.52);
  letter-spacing: 0.2em;
  text-transform: uppercase;
}
</style>
</head>
<body>
<div class="scanlines"></div>
<div class="crt-flicker"></div>

<div class="wrap">
  <header>
    <h1 class="header-title">0-1-0 // RESTORED INTERNET<span class="cursor"></span></h1>
    <div class="header-sub">fractals to infinity and beyond</div>
  </header>

  <div class="ticker-wrap">
    <div class="ticker" id="ticker"></div>
  </div>

  <main>
    <aside class="panel left">
      <h2 class="panel-title">AKASHA VAULT // FULL CAP</h2>
      <div class="panel-list">
        <div class="vault-item">
          <span class="name">American Gladiators 1992</span>
          <button class="btn-upload">UPLOAD</button>
        </div>
        <div class="vault-item">
          <span class="name">Toroid Diagram</span>
          <button class="btn-upload">UPLOAD</button>
        </div>
        <div class="vault-item">
          <span class="name">Honeybadger</span>
          <button class="btn-upload">UPLOAD</button>
        </div>
        <div class="vault-item">
          <span class="name">J5 Protocol</span>
          <button class="btn-upload">UPLOAD</button>
        </div>
      </div>
    </aside>

    <div class="monolith-wrap">
      <div class="monolith" id="monolith">
        <canvas id="monolith-canvas"></canvas>
        <div class="monolith-label">FRACTAL CORE // INFINITE</div>
      </div>
    </div>

    <aside class="panel right">
      <h2 class="panel-title">TSO CORE</h2>
      <div class="kv">
        <div class="kv-row active"><span>HB/J5</span><span>ACTIVE</span></div>
        <div class="kv-row"><span>WEIGHT</span><span>0.9</span></div>
        <div class="kv-row"><span>CORP_SHARE</span><span>0.1</span></div>
        <div class="kv-row"><span>LIMIT</span><span>-128KB ENFORCED</span></div>
      </div>
      <div class="pattern">5554443332221110111222333444555</div>
    </aside>
  </main>

  <section class="cap">
    <h2 class="cap-title">CHAPTER 11: THE CAP</h2>
    <div class="cap-buttons">
      <a href="/commons" class="btn-cap btn-commons">COMMONS FREE</a>
      <a href="/corp" class="btn-cap btn-corp">CORP 10%</a>
    </div>
    <div class="cap-remain">10/10 REMAINING</div>
  </section>

  <footer>90% mine. 10% game. All fractals witnessed.</footer>
</div>

<script>
// Balanced Market Ticker
const markets = [
  { n: 'TRUTH', v: 99.21 },
  { n: 'WITNESS', v: 97.84 },
  { n: 'ATTENTION', v: 94.17 },
  { n: 'MEMORY', v: 98.56 }
];
const ticker = document.getElementById('ticker');

function renderTicker() {
  ticker.innerHTML = '';
  const fragment = document.createDocumentFragment();
  for (let repeat = 0; repeat < 2; repeat++) {
    markets.forEach(m => {
      const item = document.createElement('div');
      item.className = 'ticker-item';
      const delta = (Math.random() * 0.06 + 0.01).toFixed(2);
      item.innerHTML = `<span class="name">${m.n}</span><span class="val">${m.v.toFixed(2)}</span><span class="delta"><span class="arrow">▲</span>${delta}</span>`;
      fragment.appendChild(item);
    });
    const sep = document.createElement('div');
    sep.className = 'ticker-item';
    sep.innerHTML = `<span style="color:var(--green-dim)">// BALANCED MARKET // NO DOWNTRENDS //</span>`;
    fragment.appendChild(sep);
  }
  ticker.appendChild(fragment);
}
renderTicker();
setInterval(() => {
  markets.forEach(m => {
    m.v = Math.min(99.99, m.v + Math.random() * 0.04 + 0.005);
  });
  renderTicker();
}, 2400);

// Vault Uploads
document.querySelectorAll('.btn-upload').forEach(btn => {
  btn.addEventListener('click', () => {
    const orig = btn.textContent;
    btn.textContent = 'WITNESSED';
    btn.disabled = true;
    btn.style.background = '#00ff00';
    btn.style.color = '#000';
    setTimeout(() => {
      btn.textContent = orig;
      btn.disabled = false;
      btn.style.background = '';
      btn.style.color = '';
    }, 1500);
  });
});

// Monolith Fractal - 5554443332221110111222333444555
const canvas = document.getElementById('monolith-canvas');
const ctx = canvas.getContext('2d', { alpha: false });
const seq = '5554443332221110111222333444555'.split('').map(Number);
let w, h, dpr;

function resize() {
  const rect = canvas.getBoundingClientRect();
  dpr = Math.min(window.devicePixelRatio || 1, 2);
  w = canvas.width = Math.floor(rect.width * dpr);
  h = canvas.height = Math.floor(rect.height * dpr);
  ctx.setTransform(1,0,0,1,0,0);
  ctx.imageSmoothingEnabled = false;
}
resize();
window.addEventListener('resize', resize);

function draw() {
  const t = performance.now() * 0.00012;
  
  ctx.fillStyle = 'rgba(0,0,0,0.14)';
  ctx.fillRect(0, 0, w, h);
  
  ctx.save();
  ctx.translate(w/2, h/2);
  ctx.rotate(t * 0.2);
  
  const offset = (t * 1.6) % 1;
  const base = Math.min(w, h) * 1.35;
  
  for (let i = 0; i < 72; i++) {
    const level = i + offset;
    const seqIdx = Math.floor(level) % seq.length;
    const digit = seq[seqIdx];
    
    const scale = Math.pow(0.913, level);
    const size = base * scale;
    
    if (size < 1.5 * dpr) break;
    if (size > base * 1.5) continue;
    
    ctx.save();
    ctx.rotate(level * 0.137 + digit * 0.07);
    
    const intensity = 1 - Math.pow(scale, 0.7);
    ctx.globalAlpha = 0.05 + intensity * 0.55;
    ctx.strokeStyle = digit >= 3 ? '#ffff00' : '#00ff00';
    ctx.lineWidth = (0.6 + digit * 0.28) * dpr;
    ctx.shadowColor = ctx.strokeStyle;
    ctx.shadowBlur = digit === 5 || digit === 0 ? 8 * dpr : 0;
    
    // Main square
    ctx.beginPath();
    const s = size/2;
    ctx.rect(-s, -s, size, size);
    ctx.stroke();
    
    // Toroid diamond for even levels
    if (digit % 2 === 0) {
      ctx.globalAlpha *= 0.6;
      ctx.beginPath();
      ctx.moveTo(0, -s);
      ctx.lineTo(s, 0);
      ctx.lineTo(0, s);
      ctx.lineTo(-s, 0);
      ctx.closePath();
      ctx.stroke();
    }
    
    // Center cross for 1 and 5
    if (digit === 1 || digit === 5) {
      ctx.globalAlpha *= 0.4;
      ctx.beginPath();
      ctx.moveTo(-s*0.3, 0); ctx.lineTo(s*0.3, 0);
      ctx.moveTo(0, -s*0.3); ctx.lineTo(0, s*0.3);
      ctx.stroke();
    }
    
    ctx.restore();
  }
  
  // Core singularity
  ctx.globalAlpha = 0.95;
  ctx.fillStyle = '#00ff00';
  ctx.shadowColor = '#00ff00';
  ctx.shadowBlur = 20 * dpr;
  ctx.beginPath();
  const pulse = 2.2 * dpr + Math.sin(t * 7) * 0.7 * dpr;
  ctx.arc(0, 0, pulse, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;
  
  // Inner nucleus
  ctx.globalAlpha = 0.6;
  ctx.fillStyle = '#ffff00';
  ctx.beginPath();
  ctx.arc(0, 0, pulse * 0.4, 0, Math.PI * 2);
  ctx.fill();
  
  ctx.restore();
  
  requestAnimationFrame(draw);
}
draw();

// Monolith interaction - click to reverberate
canvas.addEventListener('click', () => {
  const monolith = document.getElementById('monolith');
  monolith.style.boxShadow = '0 0 0 2px #000, 0 0 60px rgba(0,255,0,0.4), 0 0 160px rgba(0,255,0,0.2), inset 0 0 50px rgba(0,255,0,0.15)';
  setTimeout(() => {
    monolith.style.boxShadow = '';
  }, 300);
});
</script>
</body>
</html>"""

@app.route("/")
def monolith():
    return render_template_string(MONOLITH_HTML, 
        witness_count=len(WITNESS_LOG),
        corp_sold=len(CORP_KEYS),
        corp_remaining=CORP_CAP-len(CORP_KEYS),
        pattern=PATTERN)

@app.route("/api/status")
def status():
    return jsonify({
        "witnesses": len(WITNESS_LOG),
        "corp_sold": len(CORP_KEYS),
        "corp_remaining": CORP_CAP - len(CORP_KEYS),
        "truth": 90 + len(WITNESS_LOG)*0.01,
        "witness_weight": sum(k.get("weight",1) for k in KEYS.values()),
        "attention": 100 - len(CORP_KEYS)*2,
        "memory": len(WITNESS_LOG),
        "pattern": PATTERN,
        "hb": HB,
        "j5": J5,
        "rate": INHERITANCE_RATE
    })

@app.route("/api/media", methods=["GET","POST"])
def media():
    if request.method == "POST":
        d = request.get_json()
        if d and len(json.dumps(d)) < 5000:  # small add only
            d["ts"] = int(time.time())
            d["id"] = secrets.token_hex(3)
            MEDIA_VAULT.append(d)
            save_vault()
            witness("media_add", {"id":d["id"],"title":d.get("title")})
            return jsonify({"ok":True,"id":d["id"]})
        return jsonify({"error":"too big"}),400
    return jsonify(MEDIA_VAULT)

@app.route("/corp")
def corp():
    sold = len(CORP_KEYS); rem = CORP_CAP - sold
    if rem <= 0:
        btn = '<div style="border:2px solid #f00;padding:20px">SOLD OUT</div>'
    else:
        btn = '<stripe-buy-button buy-button-id="buy_btn_1TNuHyCgw0zJW7J1jzud6HYh" publishable-key="pk_live_51TNmRqCgw0zJW7J1mG98c3xQXo4kQlaeBFfa4fzUChBUDsTrz2NH15M3MeAvyFCga2xBO581M0hOiWsbTbGEp4Z000AH6ofQ9Q"></stripe-buy-button>'
    return f'<!DOCTYPE html><html><head><script async src="https://js.stripe.com/v3/buy-button.js"></script></head><body style="background:#000;color:#0f0;font-family:monospace;padding:40px"><h1>CORP {sold}/10</h1>{btn}<p><a href="/" style="color:#ff0">back to monolith</a></p></body></html>'

@app.route("/commons")
def commons():
    return f'<body style="background:#000;color:#0f0;font-family:monospace;padding:40px"><h1>AKASHA</h1><p>Witnesses: {len(WITNESS_LOG)}</p><p><a href="/" style="color:#ff0">monolith</a></p></body>'

@app.route("/webhook", methods=["POST"])
def webhook():
    d = request.get_json(silent=True) or {}
    if d.get("type") == "checkout.session.completed" and len(CORP_KEYS) < CORP_CAP:
        email = d.get("data",{}).get("object",{}).get("customer_details",{}).get("email","anon")
        k = "010-CORP-" + secrets.token_hex(3).upper()
        KEYS[k] = {"type":"corp"}
        CORP_KEYS.append({"key":k,"email":email})
        witness("corp_purchase",{"key":k})
    return "",200

@app.route("/witness/log")
def log(): return jsonify(WITNESS_LOG[-100:])
