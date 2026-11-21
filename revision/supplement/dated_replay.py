"""Retrospective counterfactual on dated HPC allocations with exact integer node occupancy."""
from bisect import bisect_left
import csv
from datetime import datetime,timezone
from pathlib import Path
from statistics import fmean
ROOT=Path(__file__).parent
T0=int(datetime(2022,3,7,tzinfo=timezone.utc).timestamp())
T1=T0+7*86400
BIN=1800
END=T1+4*BIN
def rows(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))

class Occupancy:
    """Range-add and range-maximum on all consecutive candidate event intervals."""
    def __init__(self,times):
        self.times=times
        n=4*len(times)
        self.val=[0]*n;self.lazy=[0]*n
    def change(self,start,end,amount):
        return self._update(1,0,len(self.times)-1,bisect_left(self.times,start),bisect_left(self.times,end),amount)
    def peak(self,start,end):
        return self._max(1,0,len(self.times)-1,bisect_left(self.times,start),bisect_left(self.times,end))
    def _update(self,i,l,r,a,b,d):
        if a>=r or b<=l:return
        if a<=l and r<=b:
            self.val[i]+=d;self.lazy[i]+=d;return
        m=(l+r)//2
        self._update(i*2,l,m,a,b,d);self._update(i*2+1,m,r,a,b,d)
        self.val[i]=self.lazy[i]+max(self.val[2*i],self.val[2*i+1])
    def _max(self,i,l,r,a,b):
        if a>=r or b<=l:return -10**9
        if a<=l and r<=b:return self.val[i]
        m=(l+r)//2
        return self.lazy[i]+max(self._max(2*i,l,m,a,b),self._max(2*i+1,m,r,a,b))

def integrated(curve,s,e):
    ans=0
    while s<e:
        left=s//BIN*BIN; stop=min(e,left+BIN)
        ans+=(stop-s)*curve[left];s=stop
    return ans

def calculate(jobs,grid,watts,width,forecast):
    flex=[(s,e,n) for s,e,n in jobs if s>=T0 and e<=T1 and n<=4 and e-s<=7200]
    times={T0,END}
    for s,e,n in jobs: times.update((max(T0,s),min(END,e)))
    for s,e,n in flex:
        for k in range(width+1):times.update((s+k*BIN,e+k*BIN))
    tree=Occupancy(sorted(times))
    for s,e,n in jobs:tree.change(max(T0,s),min(END,e),n)
    cap=tree.val[1]
    assignments=[]
    dayrows={i:[0.]*6 for i in range(7)}; moved=0;lookups=0;maxd=0
    for s,e,n in flex:
        tree.change(s,e,-n)
        candidates=[]; day=(s-T0)//86400
        for k in range(width+1):
            a,b=s+k*BIN,e+k*BIN
            lookups+=1
            if tree.peak(a,b)+n<=cap:
                curve=grid['actual'] if forecast=='oracle' else grid['archived'] if forecast=='archived' else grid['actual']
                lag=86400 if forecast=='previous_day' else 0
                candidates.append((integrated(curve,a-lag,b-lag),k))
        assert candidates
        k=min(candidates)[1]
        if width==2 and forecast=="previous_day": assignments.append((s,e,n,k*BIN))
        tree.change(s+k*BIN,e+k*BIN,n)
        assert tree.val[1]<=cap
        before=watts*n*integrated(grid['actual'],s,e)/3600000
        after=watts*n*integrated(grid['actual'],s+k*BIN,e+k*BIN)/3600000
        c=(width+1)*grid['actual'][s//BIN*BIN]/3600000
        accum=dayrows[day]
        for i,x in enumerate((1,k>0,before,after,c,k*30)):accum[i]+=x
        moved+=k>0;maxd=max(maxd,k*30)
    if assignments:
        with (ROOT/"primary_start_choices.csv").open("w",newline="") as stream:
            wr=csv.writer(stream);wr.writerow(("original_start","original_end","nodes","delay_seconds"));wr.writerows(assignments)
    a=[sum(row[i] for row in dayrows.values()) for i in range(6)]
    gross=a[2]-a[3];h=a[4]
    summary=(forecast,30*width,int(a[0]),moved,lookups,cap,a[2],a[3],gross,h,gross/h,gross-2*h,a[5]/a[0],maxd)
    return summary,[(forecast,30*width,k+datetime.fromtimestamp(T0,timezone.utc).day,int(v[0]),int(v[1]),v[2]-v[3],v[4],v[5]) for k,v in dayrows.items()]

def main():
    jobs=sorted((int(r['start_epoch_utc']),int(r['end_epoch_utc']),int(r['nodes'])) for r in rows('archer2_allocations.csv'))
    raw=rows('gb_intensity.csv')
    grid={k:{int(r['from_epoch_utc']):int(r[col]) for r in raw} for k,col in [('actual','actual_gCO2_per_kWh'),('archived','archived_forecast_gCO2_per_kWh')]}
    meter=rows('archer2_meter_calibration.csv')[0];w=float(meter['median_W_per_node'])
    totals=[];daily=[]
    for f in ('previous_day','archived','oracle'):
        for h in (0,1,2,4):
            a,b=calculate(jobs,grid,w,h,f);totals.append(a);daily+=b
    for name,header,rs in [('dated_results.csv','signal slack_min eligible moved lookups max_concurrent_nodes original_gCO2 shifted_gCO2 gross_saving_gCO2 grams_per_J_per_lookup break_even_J_per_lookup net_at_2J_gCO2 mean_delay_min max_delay_min',totals),('dated_daily.csv','signal slack_min day_March2022 eligible moved gross_saving_gCO2 grams_per_J_per_lookup total_delay_min',daily)]:
        with (ROOT/name).open('w',newline='') as f:
            wr=csv.writer(f);wr.writerow(header.split());wr.writerows(rs)
    print('dated allocations:',len(jobs),'power calibration:',w)
    for r in totals:print(r[0],r[1],r[2],r[3],r[5],*(round(a,2) for a in r[8:14]))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repeat',action='store_true')
    if parser.parse_args().repeat:
        ROOT=ROOT/'repeat_week';T0+=7*86400;T1+=7*86400;END+=7*86400
    main()
