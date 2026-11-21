"""Chronological, capacity-limited replay. The policy receives only release time, nodes and past intensities."""
import csv
import hashlib
import heapq
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

ROOT=Path(__file__).resolve().parents[1]
CAPACITY=5860
STEP=1800
WEEK=7*86400

def load(name):
    with (ROOT/'inputs'/name).open() as f:return list(csv.DictReader(f))

def get_grid():
    g={}
    for name in ('week1/gb_intensity.csv','week2/gb_intensity.csv','drain_intensity.csv'):
        for row in load(name):
            key=int(row['from_epoch_utc']); val=int(row['actual_gCO2_per_kWh'])
            assert key not in g or g[key]==val
            g[key]=val
    assert sorted(g)==list(range(min(g),max(g)+1,STEP))
    return g

def opt_in(index,week,percent):
    # Cohort assignment excludes duration. Nested 25, 50, 100 percent cohorts.
    bucket=int.from_bytes(hashlib.sha256(f'{week}/{index}'.encode()).digest()[:4],'big')%100
    return bucket<percent

def proposal(t,offsets,grid):
    base=(t//STEP)*STEP-86400
    return t+min(offsets,key=lambda off:grid[base+off])

def queue_sim(rows,start,end,delays,share,grid,week):
    carry=[(e,n) for s,e,n in rows if s<start<e]
    arrivals=[(s,n,e-s) for s,e,n in rows if start<=s<end]
    occupied=sum(n for e,n in carry);peak=occupied
    ends=list(carry); heapq.heapify(ends)
    ready=[]; pending=deque(); pos=0; starts={};checks={}
    INF=10**20
    while pos<len(arrivals) or ready or pending:
        t=min(arrivals[pos][0] if pos<len(arrivals) else INF,ready[0][0] if ready else INF,ends[0][0] if ends else INF)
        assert t!=INF
        while ends and ends[0][0]==t: occupied-=heapq.heappop(ends)[1]
        while pos<len(arrivals) and arrivals[pos][0]==t:
            _,n,_=arrivals[pos]
            participate=n<=4 and share>0 and opt_in(pos,week,share)
            eligible=proposal(t,delays,grid) if participate else t
            if participate:checks[pos]=len(delays)
            heapq.heappush(ready,(eligible,pos));pos+=1
        while ready and ready[0][0]==t:pending.append(heapq.heappop(ready)[1])
        while pending:
            j=pending[0];_,n,runtime=arrivals[j]
            if occupied+n>CAPACITY:break
            pending.popleft();starts[j]=t;occupied+=n;peak=max(peak,occupied)
            # Runtime only determines when the environment informs the dispatcher of completion.
            heapq.heappush(ends,(t+runtime,n))
    assert len(starts)==len(arrivals) and peak<=CAPACITY
    return arrivals,starts,checks,peak

def integrated(t,duration,grid):
    total=0
    while duration>0:
        b=(t//STEP)*STEP; d=min(duration,b+STEP-t);total+=grid[b]*d; t+=d;duration-=d
    return total

def main():
    grid=get_grid()
    watts=float(load('archer2_meter_calibration.csv')[0]['median_W_per_node'])
    results=[];days=[]
    for week,date in enumerate(('2022-03-07','2022-03-14'),1):
        start=int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp())
        rows=sorted([(int(x['start_epoch_utc']),int(x['end_epoch_utc']),int(x['nodes'])) for x in load(f'week{week}/archer2_allocations.csv')],key=lambda r:(r[0],r[2]))
        # Stable order on tied start+node preserves input order. Duration is never a scheduling key.
        jobs,base,_,_=queue_sim(rows,start,start+WEEK,[0],0,grid,week)
        assert all(base[j]==s for j,(s,n,d) in enumerate(jobs)), 'unshifted dispatch failed to recover every recorded start'
        original={j:n*watts/3.6e6*integrated(s,d,grid) for j,(s,n,d) in enumerate(jobs)}
        for share in (25,50,100):
            for horizon in (30,60):
                offsets=list(range(0,60*horizon+1,STEP))
                _,actual,checks,peak=queue_sim(rows,start,start+WEEK,offsets,share,grid,week)
                lookup_cost=sum(k*grid[(jobs[j][0]//STEP)*STEP]/3.6e6 for j,k in checks.items())
                savings={j:original[j]-n*watts/3.6e6*integrated(actual[j],d,grid) for j,(s,n,d) in enumerate(jobs)}
                gross=sum(savings.values()); eligible=sum(original[j] for j in checks)
                moved=[j for j,(s,n,d) in enumerate(jobs) if actual[j]>s]
                delay=[(actual[j]-s)/60 for j,(s,n,d) in enumerate(jobs)]
                ext=[j for j in moved if j not in checks]
                eligible_delay=mean(delay[j] for j in checks)
                results.append((week,horizon,share,len(jobs),len(checks),len(moved),len(ext),peak,sum(checks.values()),sum(original.values()),eligible,gross,100*gross/sum(original.values()),100*sum(savings[j] for j in checks)/eligible,mean(delay),eligible_delay,max(delay),lookup_cost,gross/lookup_cost))
                for day in range(7):
                    subset=[j for j,(s,n,d) in enumerate(jobs) if (s-start)//86400==day]
                    days.append((week,horizon,share,day+1,len(subset),sum(savings[j] for j in subset),mean(delay[j] for j in subset)))
    for name,headers,data in [('replay.csv',['week','max_proposed_delay_min','opt_in_percent','all_jobs','opted_jobs','moved_jobs','delayed_nonparticipants','peak_nodes','candidate_reads','baseline_all_g','baseline_opted_g','gross_saved_all_g','pct_all','pct_opted','mean_all_delay_min','mean_opted_delay_min','max_realized_delay_min','controller_g_per_J_per_read','break_even_J_per_read'],results),('daily.csv',['week','max_proposed_delay_min','opt_in_percent','release_day','jobs','gross_saved_g','mean_delay_min'],days)]:
        with (ROOT/'outputs'/name).open('w',newline='') as f:
            w=csv.writer(f);w.writerow(headers);w.writerows(data)

if __name__=='__main__':main()
