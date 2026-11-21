"""Compare the real-time policy with perfect-information dispatch and a protected-start ceiling.

All original jobs use the same meter calibration, realized duration, half-hour grid, and
three proposed starts as the lagged policy. Output sums include all weekly releases.
"""
import csv
from collections import defaultdict
from datetime import datetime, timezone
from math import isclose
from statistics import mean
from dispatch import CAPACITY, ROOT, STEP, WEEK, get_grid, load, queue_sim

OFFSETS = (0, STEP, 2 * STEP)


class MaxOccupancy:
    """Range add and range max on a compressed event timeline, with lazy propagation."""
    def __init__(self, loads):
        n = 1
        while n < len(loads):
            n *= 2
        self.size = n
        self.maximum = [0] * (2 * n)
        self.delta = [0] * (2 * n)
        self.maximum[n:n+len(loads)] = loads
        for j in range(n-1, 0, -1):
            self.maximum[j] = max(self.maximum[2*j:2*j+2])

    def query(self, left, right, change=0):
        def visit(node, lo, hi):
            if left <= lo and hi <= right:
                previous = self.maximum[node]
                self.maximum[node] += change
                self.delta[node] += change
                return previous
            mid = (lo + hi) // 2
            values = []
            if left < mid:
                values.append(visit(2*node, lo, mid))
            if right > mid:
                values.append(visit(2*node+1, mid, hi))
            self.maximum[node] = self.delta[node] + max(self.maximum[2*node:2*node+2])
            return self.delta[node] + max(values)
        assert 0 <= left < right <= self.size
        return visit(1, 0, self.size)


def census(jobs, times, carry, week_start):
    events = defaultdict(int)
    for end,nodes in carry:
        events[week_start] += nodes
        events[end] -= nodes
    for i, (_,n,d) in enumerate(jobs):
        events[times[i]] += n
        events[times[i]+d] -= n
    loads = []
    used = 0
    for t in sorted(events):
        used += events[t]
        loads.append(used)
    assert min(loads) >= 0 and loads[-1] == 0
    return max(loads)


def calendar(jobs, carry, start, best):
    changes = defaultdict(int)
    for e,n in carry:
        changes[start] += n
        changes[e] -= n
    for i,(s,n,d) in enumerate(jobs):
        changes[s] += n
        changes[s+d] -= n
        if i in best:
            for k in OFFSETS[1:]:
                changes[s+k] += 0
                changes[s+d+k] += 0
    keys = sorted(changes)
    index = {t:j for j,t in enumerate(keys)}
    load = 0
    series = []
    for t in keys:
        load += changes[t]
        series.append(load)
    assert load == 0 and max(series) <= CAPACITY
    return index, MaxOccupancy(series)


def protected_schedule(jobs, carry, start, improvement, first_choices):
    # Begin at the feasible published timetable. Nonparticipants and carry-in never move.
    if census(jobs,first_choices,carry,start) <= CAPACITY:
        return first_choices
    pref = {i:sorted(OFFSETS,key=lambda k:(-gain[k], k)) for i,gain in improvement.items()}
    order = sorted(pref, key=lambda i:(-improvement[i][pref[i][0]], i))
    index, curve = calendar(jobs, carry, start, pref)
    result = {i:s for i,(s,_,_) in enumerate(jobs)}
    for i in order:
        s,n,d = jobs[i]
        for k in pref[i]:
            if k == 0:
                break
            # A later interval removes a leading piece and adds a disjoint trailing piece.
            trail_left, trail_right = index[max(s+k,s+d)], index[s+d+k]
            if curve.query(trail_left, trail_right) + n <= CAPACITY:
                curve.query(index[s],index[min(s+k,s+d)],-n)
                curve.query(trail_left,trail_right,n)
                result[i] = s+k
                break
    assert curve.maximum[1] <= CAPACITY
    return result


def study():
    grid = get_grid()
    power = float(load('archer2_meter_calibration.csv')[0]['median_W_per_node'])
    origin = min(grid)
    bands = sorted(grid)
    end = bands[-1] + STEP
    cumulative = [0]
    for t in bands:
        cumulative.append(cumulative[-1] + STEP * grid[t])

    def area(t):
        assert origin <= t <= end
        slot, rem = divmod(t-origin, STEP)
        return cumulative[slot] + (rem * grid[origin+slot*STEP] if rem else 0)

    def mass(t,n,d):
        return n * (area(t+d)-area(t)) * power / 3.6e9   # kg CO2

    out = []
    for week, date in enumerate(('2022-03-07', '2022-03-14'),1):
        start = int(datetime.fromisoformat(date).replace(tzinfo=timezone.utc).timestamp())
        rows = sorted(((int(r['start_epoch_utc']), int(r['end_epoch_utc']), int(r['nodes']))
                       for r in load(f'week{week}/archer2_allocations.csv')),key=lambda row:(row[0], row[2]))
        carry = [(e,n) for s,e,n in rows if s < start < e]
        jobs, lagged, opted, lag_peak = queue_sim(rows,start,start+WEEK,OFFSETS,100,grid,week)
        initial = [mass(s,n,d) for s,n,d in jobs]
        total = sum(initial)
        eligible = sum(initial[i] for i in opted)
        gains = {i:{k:initial[i]-mass(s+k,n,d) for k in OFFSETS}
                 for i,(s,n,d) in enumerate(jobs) if i in opted}
        best = {i:jobs[i][0] + max(OFFSETS, key=lambda k:(v[k],-k)) for i,v in gains.items()}
        ideal = {i:best.get(i,s) for i,(s,_,_) in enumerate(jobs)}
        _, fifo, _, fifo_peak = queue_sim(rows,start,start+WEEK,OFFSETS,100,grid,week,offline_targets=best)
        feasible = protected_schedule(jobs,carry,start,gains,ideal)
        # Same protected-start opportunity class, ordered by the previous day's decline.
        # The offline capacity repair uses the original calendar for both comparisons.
        forecast = {}
        forecast_ideal = {i:s for i,(s,_,_) in enumerate(jobs)}
        for i in opted:
            s,n,_ = jobs[i]
            yesterday = (s//STEP)*STEP - 86400
            forecast[i] = {k:n*(grid[yesterday]-grid[yesterday+k]) for k in OFFSETS}
            forecast_ideal[i] = s + max(OFFSETS,key=lambda k:(forecast[i][k],-k))
        yesterday_protected = protected_schedule(jobs,carry,start,forecast,forecast_ideal)
        for method,times in [('previous_day_fifo',lagged),('clairvoyant_fifo',fifo),
                             ('protected_previous_day',yesterday_protected),('protected_feasible',feasible),('protected_ceiling',ideal)]:
            peak = census(jobs,times,carry,start)
            if method != 'protected_ceiling':
                assert peak <= CAPACITY
            if method in ('previous_day_fifo','clairvoyant_fifo'):
                assert peak == (lag_peak if method=='previous_day_fifo' else fifo_peak)
            delta = [t-s for (_,t),(s,_,_) in zip(sorted(times.items()),jobs)]
            assert all(x>=0 for x in delta)
            outsider = [i for i in range(len(jobs)) if i not in opted]
            if method.startswith('protected'):
                assert all(delta[i] in OFFSETS for i in opted) and all(delta[i]==0 for i in outsider)
            reductions = [initial[i]-mass(times[i],n,d) for i,(_,n,d) in enumerate(jobs)]
            participant = sum(reductions[i] for i in opted)
            external = sum(reductions[i] for i in outsider)
            net = sum(reductions)
            assert isclose(net,participant+external,abs_tol=1e-8)
            out.append(dict(week=week,method=method,all_jobs=len(jobs),participating_jobs=len(opted),
                       baseline_all_kg=total,baseline_part_kg=eligible,
                       saved_part_kg=participant,saved_nonpart_kg=external,saved_all_kg=net,
                       pct_all=100*net/total,pct_part=100*participant/eligible,
                       delayed_nonpart=sum(delta[i]>0 for i in outsider),mean_delay_min=mean(delta)/60,
                       max_delay_min=max(delta)/60,peak_nodes=peak,
                       over_60min_jobs=sum(x>2*STEP for x in delta)))
        upper = out[-1]['saved_all_kg']
        assert out[-2]['saved_all_kg'] <= upper+1e-7
        assert isclose(upper,sum(max(v.values()) for v in gains.values()),abs_tol=1e-7)
    return out


if __name__ == '__main__':
    out = study()
    dst = ROOT/'outputs'/'opportunity.csv'
    with dst.open('w',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows(out)
    for row in out:
        print(row['week'],row['method'],
              *(round(row[k],6) for k in ('saved_part_kg','saved_nonpart_kg','saved_all_kg','pct_all','pct_part','peak_nodes','mean_delay_min','max_delay_min','over_60min_jobs')))
