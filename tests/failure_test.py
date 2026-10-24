"""Failure injection: SIGKILL the app (whole process group), detect via 1s health probe
(2 consecutive failures = alert), restart (what `restart: always` / ECS does), verify with /health
+ a real API call. TTR = detection + diagnosis + recovery + verification."""
import os, signal, subprocess, time, requests, json
B="http://127.0.0.1:8000"
env=dict(os.environ, DB_PATH="/tmp/hosp/appointments.db")
def start(): return subprocess.Popen(["gunicorn","-w","4","-b","127.0.0.1:8000","--chdir","app","app:app"],env=env,start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def up():
    try: return requests.get(B+"/health",timeout=1).status_code==200
    except Exception: return False
def wait_up():
    while not up(): time.sleep(0.05)
p=start(); wait_up(); runs=[]
for i in range(1,6):
    t0=time.time(); os.killpg(p.pid,signal.SIGKILL); p.wait()
    fails=0
    while fails<2:
        fails = 0 if up() else fails+1; time.sleep(1)
    td=time.time()
    time.sleep(0.5); tdiag=time.time()
    p=start(); wait_up(); tr=time.time()
    ok=requests.post(B+"/api/appointments",json={"patient":"verify","doctor":"Dr. Iyer","slot":"11:00"}).status_code==201
    tv=time.time()
    r=dict(run=i,detect=round(td-t0,1),diagnose=round(tdiag-td,1),recover=round(tr-tdiag,1),verify=round(tv-tr,1),ttr=round(tv-t0,1),verified=ok)
    print(r); runs.append(r)
os.killpg(p.pid,signal.SIGKILL)
avg=lambda k: round(sum(r[k] for r in runs)/len(runs),1)
s=dict(runs=runs,avg_ttr=avg("ttr"),max_ttr=max(r["ttr"] for r in runs),avg_detect=avg("detect"),avg_recover=avg("recover"))
print(s); json.dump(s,open("tests/failure_result.json","w"),indent=1)
