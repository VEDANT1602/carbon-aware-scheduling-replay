"""Independent cumulative-integral and occupancy sweeps for the full-eligibility 60-minute policy."""
import csv
from datetime import datetime, timezone
from math import isclose
from dispatch import ROOT,get_grid,load,queue_sim,STEP,WEEK,CAPACITY

g=get_grid(); low=min(g);cum={low:0}
for t in sorted(g):cum[t+STEP]=cum[t]+STEP*g[t]
def area(t):
    k=t//STEP*STEP
    return cum[k]+(t-k)*g.get(k,0)

with (ROOT/'outputs'/'replay.csv').open() as h:reports=list(csv.DictReader(h))
power=float(load('archer2_meter_calibration.csv')[0]['median_W_per_node'])
for week,date in enumerate(('2022-03-07','2022-03-14'),1):
    start=int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp())
    rows=sorted([(int(r['start_epoch_utc']),int(r['end_epoch_utc']),int(r['nodes'])) for r in load(f'week{week}/archer2_allocations.csv')],key=lambda a:(a[0],a[2]))
    jobs,times,checks,_=queue_sim(rows,start,start+WEEK,[0,STEP,2*STEP],100,g,week)
    events=[]
    for s,e,n in rows:
        if s<start<e:events+=[(start,n),(e,-n)]
    balance=0
    for i,(s,n,d) in enumerate(jobs):
        t=times[i]; events.extend([(t,n),(t+d,-n)])
        balance+=n*((area(s+d)-area(s))-(area(t+d)-area(t)))
    occupancy=peak=0
    for _,change in sorted(events):
        occupancy+=change;peak=max(peak,occupancy);assert 0<=occupancy<=CAPACITY
    rec=next(r for r in reports if int(r['week'])==week and int(r['opt_in_percent'])==100 and int(r['max_proposed_delay_min'])==60)
    assert isclose(balance*power/3.6e6,float(rec['gross_saved_all_g']),rel_tol=1e-11)
    assert peak==int(rec['peak_nodes']) and occupancy==0
    print('Week',week,'jobs',len(jobs),'peak',peak,'saving g',balance*power/3.6e6)
