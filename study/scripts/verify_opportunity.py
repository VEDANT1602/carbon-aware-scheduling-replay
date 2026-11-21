"""Recompute independent energy upper bounds and check discrete feasibility on exact toy cases."""
import csv
import itertools
from datetime import datetime, timezone
from math import isclose
import random
from dispatch import CAPACITY, ROOT, STEP, WEEK, get_grid, integrated, load, queue_sim
from opportunity import OFFSETS, protected_schedule


def peak_by_segments(jobs, offsets):
    points = sorted({t for (s,n,d),k in zip(jobs,offsets) for t in (s+k,s+k+d)})
    return max(sum(n for (s,n,d),k in zip(jobs,offsets) if s+k<=t<s+k+d) for t in points)


def check_examples():
    # Half-open overlap, boundary ties, overlapping relocations and occupied starts.
    rand = random.Random(20261121)
    tight = 0
    for _ in range(64):
        jobs = [(i*STEP,rand.randrange(3100,5000),rand.randrange(1,STEP+1)) for i in range(5)]
        gains = {i:{0:0,STEP:rand.randrange(-3,10),2*STEP:rand.randrange(-3,10)} for i in range(5)}
        favorite = {i:s+max(OFFSETS,key=lambda k:(gains[i][k],-k)) for i,(s,_,_) in enumerate(jobs)}
        found = protected_schedule(jobs,[],0,gains,favorite)
        chosen = [found[i]-s for i,(s,_,_) in enumerate(jobs)]
        assert peak_by_segments(jobs,chosen)<=CAPACITY
        def value(ks):
            return sum(gains[i][k] for i,k in enumerate(ks))
        optimum = max(value(ks) for ks in itertools.product(OFFSETS,repeat=5) if peak_by_segments(jobs,ks)<=CAPACITY)
        assert value(chosen) <= optimum <= sum(max(g.values()) for g in gains.values())
        tight += value(chosen)==optimum
    print('64 exact five-job schedules checked; feasible greedy matched exact optimum',tight,'times.')


def check_study():
    grid = get_grid()
    power = float(load('archer2_meter_calibration.csv')[0]['median_W_per_node'])
    with (ROOT/'outputs/opportunity.csv').open() as f:
        table = {(int(r['week']),r['method']):r for r in csv.DictReader(f)}
    for w,date in enumerate(('2022-03-07','2022-03-14'),1):
        start = int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp())
        rows = sorted(((int(r['start_epoch_utc']),int(r['end_epoch_utc']),int(r['nodes'])) for r in load(f'week{w}/archer2_allocations.csv')),key=lambda row:(row[0],row[2]))
        jobs,times,participants,_ = queue_sim(rows,start,start+WEEK,OFFSETS,100,grid,w)
        bound = part = other = 0
        for i,(s,n,d) in enumerate(jobs):
            old = integrated(s,d,grid)
            delta = power*n*(old - integrated(times[i],d,grid))/3.6e9
            if i in participants:
                part += delta
                least = min(integrated(s+k,d,grid) for k in OFFSETS)
                bound += power*n*(old-least)/3.6e9
            else:
                other += delta
        for method,key,v in [('protected_ceiling','saved_all_kg',bound),
                             ('previous_day_fifo','saved_part_kg',part),
                             ('previous_day_fifo','saved_nonpart_kg',other)]:
            assert isclose(v,float(table[w,method][key]),rel_tol=1e-12,abs_tol=1e-8)
        if w==2:
            assert int(table[w,'protected_ceiling']['peak_nodes'])<=CAPACITY
        print('Week',w,'upper bound, kg:',round(bound,6),'lagged participant and external kg:',round(part,6),round(other,6))


if __name__ == '__main__':
    check_examples()
    check_study()
