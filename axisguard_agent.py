import psutil
import time
import json
import os
from datetime import datetime

# FINAL CLEAN LIST - cmd.exe REMOVED so normal Command Prompt won't trigger alerts
SUSPICIOUS = ["mimikatz.exe", "psexec.exe", "psexec64.exe", "nmap.exe", "netcat.exe", "nc.exe", "meterpreter.exe", "keylogger.exe"]

print("AxisGuard X - Agent Started - FINAL VERSION")

seen = set()
alerts = []

# Load existing alerts if file exists (so restart doesn't lose them)
if os.path.exists("alerts.json"):
    try:
        with open("alerts.json") as f:
            alerts = json.load(f)
            for a in alerts:
                seen.add(a["pid"])
    except:
        alerts = []

def save_alerts():
    with open("alerts.json", "w") as f:
        json.dump(alerts, f)

try:
    while True:
        # 1. Check for NEW suspicious processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                name = (proc.info['name'] or "").lower()
                if pid in seen:
                    continue
                seen.add(pid)
                for bad in SUSPICIOUS:
                    if name == bad:
                        alert = {"pid": pid, "name": name, "time": datetime.now().strftime('%H:%M:%S')}
                        print(f"[!] ALERT {alert['time']} - {name} (PID {pid})")
                        alerts.append(alert)
                        save_alerts()
            except:
                pass

        # 2. AUTO-CLEAN - Remove alerts for dead processes
        alive_alerts = []
        changed = False
        for a in alerts:
            if psutil.pid_exists(a["pid"]):
                alive_alerts.append(a)
            else:
                print(f"[+] Cleaned - {a['name']} (PID {a['pid']}) is gone, removing from Dashboard")
                changed = True
        if changed:
            alerts = alive_alerts
            save_alerts()

        print(f"[+] Running... {datetime.now().strftime('%H:%M:%S')} - {len(seen)} seen, {len(alerts)} active alerts")
        time.sleep(5)
except KeyboardInterrupt:
    print("\nAxisGuard stopped.")