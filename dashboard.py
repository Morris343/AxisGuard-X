from flask import Flask, render_template_string
import json, os, psutil
from datetime import datetime

app = Flask(__name__)

HTML = """
<html><head><meta http-equiv="refresh" content="5"><style>
body{background:#0a0a2e;color:white;font-family:Arial;padding:30px}
h1{color:#00ff66}
h2{margin-top:30px}
.alert{background:#ff3333;padding:15px;margin:10px 0;border-radius:8px;display:flex;justify-content:space-between;align-items:center}
.killed{background:#1a5c2a;padding:12px;margin:8px 0;border-radius:8px;display:flex;justify-content:space-between}
button{padding:8px 15px;border:none;border-radius:5px;cursor:pointer;font-weight:bold}
.clear{background:#555;color:white;padding:8px 15px;text-decoration:none;border-radius:5px;font-size:13px}
</style></head><body>
<h1>AxisGuard X - Live Dashboard</h1>
<p>Auto-refreshes every 5 seconds</p>

<h2>🔴 Active Threats</h2>
{% if alerts %}
  {% for a in alerts %}
    <div class="alert"><span>ALERT {{a.time}} - {{a.name}} (PID {{a.pid}})</span>
    <a href="/kill/{{a.pid}}"><button>KILL</button></a></div>
  {% endfor %}
{% else %}
  <p style="color:#00ff66">✅ System Secure - No Active Threats</p>
{% endif %}

<h2>✅ Killed History - {{ killed|length }} threats stopped</h2>
<a class="clear" href="/clear-history">Clear History</a><br><br>
{% for k in killed %}
  <div class="killed"><span>✅ KILLED {{k.kill_time}} - {{k.name}} (PID {{k.pid}})</span><span>Was detected at {{k.time}}</span></div>
{% endfor %}
{% if not killed %}
  <p style="color:#888">No kills yet - run a test!</p>
{% endif %}
</body></html>
"""

def load_alerts():
    if not os.path.exists("alerts.json"):
        return []
    try:
        with open("alerts.json") as f:
            return json.load(f)
    except:
        return []

def load_killed():
    if not os.path.exists("killed.json"):
        return []
    try:
        with open("killed.json") as f:
            return json.load(f)
    except:
        return []

@app.route("/")
def home():
    return render_template_string(HTML, alerts=load_alerts(), killed=load_killed())

@app.route("/kill/<int:pid>")
def kill(pid):
    alerts = load_alerts()
    target = None
    for a in alerts:
        if a["pid"] == pid:
            target = a
            break
    try:
        psutil.Process(pid).kill()
        print(f"Killed PID {pid}")
    except:
        print(f"PID {pid} already gone")
    alerts = [a for a in alerts if a["pid"] != pid]
    with open("alerts.json", "w") as f:
        json.dump(alerts, f)
    if target:
        killed = load_killed()
        killed.insert(0, {"pid": target["pid"], "name": target["name"], "time": target["time"], "kill_time": datetime.now().strftime('%H:%M:%S')})
        with open("killed.json", "w") as f:
            json.dump(killed, f)
    return render_template_string(HTML, alerts=alerts, killed=load_killed())

@app.route("/clear-history")
def clear_history():
    with open("killed.json", "w") as f:
        json.dump([], f)
    return render_template_string(HTML, alerts=load_alerts(), killed=[])

if __name__ == "__main__":
    app.run(port=8000, debug=True)