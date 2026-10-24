import time, json, statistics, requests
from concurrent.futures import ThreadPoolExecutor
BASE="http://127.0.0.1:8000"; USERS,REQS=50,40
def user(i):
    s=requests.Session(); out=[]; e=0
    for j in range(REQS):
        t=time.perf_counter()
        try:
            if j%4==0: r=s.post(BASE+"/api/appointments",json={"patient":f"P{i}-{j}","doctor":"Dr. Sharma","slot":"10:30"},timeout=10)
            elif j%4==1: r=s.get(BASE+"/api/appointments",timeout=10)
            else: r=s.get(BASE+"/api/doctors",timeout=10)
            if r.status_code>=400: e+=1
        except Exception: e+=1
        out.append((time.perf_counter()-t)*1000)
    return out,e
t0=time.perf_counter()
with ThreadPoolExecutor(USERS) as ex: res=list(ex.map(user,range(USERS)))
dur=time.perf_counter()-t0
lat=sorted(x for o,_ in res for x in o); errs=sum(e for _,e in res); n=len(lat)
p=lambda q: lat[min(n-1,int(q*n))]
out=dict(requests=n,errors=errs,duration_s=round(dur,2),rps=round(n/dur,1),avg_ms=round(statistics.mean(lat),1),p95_ms=round(p(.95),1),p99_ms=round(p(.99),1),success_pct=round(100*(n-errs)/n,2))
print(json.dumps(out)); json.dump(out,open("tests/load_result.json","w"))
