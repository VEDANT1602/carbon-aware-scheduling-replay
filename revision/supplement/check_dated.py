"""Independently sweep the realized primary assignments and integrate their half-hour energy."""
from collections import Counter
import csv
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).parent
def read(file):
    with (ROOT/file).open() as f:return list(csv.DictReader(f))
def max_nodes(events):
    total=peak=0
    for t,d in sorted(events.items()):
        total+=d;peak=max(peak,total)
    assert total==0
    return peak
def integrate(a,b,curve):
    out=0
    for slot in range(a//1800,(b-1)//1800+1):
        left=slot*1800
        out+=curve[left]*(min(b,left+1800)-max(a,left))
    return out
def main(repeat=False):
    start=int(datetime(2022,3,14 if repeat else 7,tzinfo=timezone.utc).timestamp()); end=start+7*86400+7200
    grid={int(r['from_epoch_utc']):int(r['actual_gCO2_per_kWh']) for r in read('gb_intensity.csv')}
    power=float(read('archer2_meter_calibration.csv')[0]['median_W_per_node'])
    original=Counter();eligible=Counter()
    for r in read('archer2_allocations.csv'):
        a,b,n=map(int,r.values())
        if a>=start and b<=end-7200 and n<=4 and b-a<=7200:
            eligible[(a,b,n)]+=1
        original[max(a,start)]+=n;original[min(b,end)]-=n
    shifted=original.copy()
    gross=coef=0.;moved=0
    choices=read('primary_start_choices.csv')
    for r in choices:
        a,b,n,d=map(int,r.values());assert d in (0,1800,3600) and eligible[(a,b,n)]>0
        eligible[(a,b,n)]-=1;shifted[a]-=n;shifted[b]+=n;shifted[a+d]+=n;shifted[b+d]-=n
        gross+=n*power*(integrate(a,b,grid)-integrate(a+d,b+d,grid))/3600000
        coef+=3*grid[a//1800*1800]/3600000;moved+=d>0
    assert not any(eligible.values())
    case=next(r for r in read('dated_results.csv') if r['signal']=='previous_day' and r['slack_min']=='60')
    assert len(choices)==int(case['eligible']) and moved==int(case['moved'])
    assert max_nodes(shifted)<=max_nodes(original)==int(case['max_concurrent_nodes'])
    assert abs(gross-float(case['gross_saving_gCO2']))<1e-5
    assert abs(gross/coef-float(case['break_even_J_per_lookup']))<1e-4
    print('Independent event and carbon audit:',len(choices),'allocations;',moved,'rescheduled;',max_nodes(shifted),'peak nodes;',round(gross/coef,2),'J/candidate.')
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--repeat',action='store_true')
    repeat=parser.parse_args().repeat
    if repeat:ROOT=ROOT/'repeat_week'
    main(repeat)
