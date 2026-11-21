"""Local in-memory decision time; paired package-energy metering when Linux RAPL is readable."""
import argparse
import csv
import os
import platform
from pathlib import Path
from statistics import median
from time import perf_counter_ns,process_time_ns

from dispatch import ROOT,get_grid,load,proposal

def energy_counter():
    for path in sorted(Path('/sys/class/powercap').glob('intel-rapl*/energy_uj')):
        try:
            if 'package' in (path.parent/'name').read_text().lower():
                int(path.read_text());return path
        except OSError:continue

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repeats',type=int,default=13)
    args=parser.parse_args()
    rows=load('week1/archer2_allocations.csv')
    begin=1646611200
    arrivals=[int(r['start_epoch_utc']) for r in rows if begin<=int(r['start_epoch_utc'])<begin+7*86400 and int(r['nodes'])<=4]
    grid=get_grid(); offsets=(0,1800,3600); counter=energy_counter()
    def batch(active):
        ej=int(counter.read_text()) if counter else None
        wall=perf_counter_ns();cpu=process_time_ns()
        total=0
        for t in arrivals:total+=proposal(t,offsets,grid) if active else t
        cpu=process_time_ns()-cpu;wall=perf_counter_ns()-wall
        if counter:
            end=int(counter.read_text());mod=int((counter.parent/'max_energy_range_uj').read_text()); energy=(end-ej)%mod
        else:energy=None
        return wall,cpu,energy,total
    batch(True);batch(False)
    results=[]
    for i in range(args.repeats):
        order=(True,False) if i%2==0 else (False,True)
        times={k:batch(k) for k in order}; a,b=times[True],times[False]
        assert a[-1]>=b[-1]
        results.append((i+1,len(arrivals),order[0],a[0],b[0],(a[0]-b[0])/len(arrivals),a[1],b[1],(a[1]-b[1])/len(arrivals),a[2],b[2],(a[2]-b[2])/len(arrivals) if counter else '',str(counter or ''),platform.python_version(),platform.machine()))
    with (ROOT/'outputs'/'benchmark.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['repeat','proposals','active_first','active_ns','control_ns','net_wall_ns_per_proposal','active_cpu_ns','control_cpu_ns','net_cpu_ns_per_proposal','active_package_uJ','control_package_uJ','net_package_uJ_per_proposal','package_counter','python','machine']);w.writerows(results)
    print('median incremental ns/proposal (wall, cpu):',median(r[5] for r in results),median(r[8] for r in results),'; package counter:',counter)
if __name__=='__main__':main()
