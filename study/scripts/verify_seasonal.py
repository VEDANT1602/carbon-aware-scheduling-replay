"""Check matched baselines and capacity-relaxed ceilings by explicit half-hour integration."""
import argparse
import csv
from datetime import date
from math import isclose
from pathlib import Path

from dispatch import ROOT, STEP, load, integrated
from seasonal import DAY, OFFSETS, allocation_windows, epoch, grids, preferences


def read(name):
    with (ROOT/'outputs'/name).open(newline='') as f:
        return list(csv.DictReader(f))


def audit(cache):
    grid, _ = grids(cache)
    scale = float(load('archer2_meter_calibration.csv')[0]['median_W_per_node']) / 3.6e9
    rows = read('seasonal.csv')
    dates = read('seasonal_windows.csv')
    windows = allocation_windows(cache)
    old = {(r['week'], r['method']):r for r in read('opportunity.csv')}
    for window in dates:
        day = window['release_monday']
        start = epoch(date.fromisoformat(day))
        selections = {r['method']:r for r in rows if r['release_monday']==day}
        if window['status'] != 'complete':
            assert not selections
            continue
        jobs = [(s,n,e-s) for s,e,n in windows[start] if s>=start]
        assert len(jobs)==int(window['releases'])
        baseline = upper = part_baseline = 0
        for s,n,d in jobs:
            initial = integrated(s,d,grid)
            baseline += n * initial
            if n <= 4:
                part_baseline += n * initial
                best = min(initial,*(integrated(s+k,d,grid) for k in OFFSETS[1:]))
                upper += n * (initial - best)
        assert len(selections)==8
        cap = float(selections['ceiling']['saved_all_kg'])
        assert isclose(cap, upper*scale, abs_tol=1e-7)
        for name,r in selections.items():
            total, part, other = (float(r[k]) for k in ['saved_all_kg','saved_participant_kg','saved_nonparticipant_kg'])
            assert isclose(baseline*scale,float(r['all_baseline_kg']),abs_tol=1e-6)
            assert isclose(part_baseline*scale,float(r['participant_baseline_kg']),abs_tol=1e-6)
            assert isclose(total, part+other,abs_tol=1e-7)
            if name.startswith('protected_'):
                assert total <= cap + 1e-7 and abs(other) < 1e-7
            if name != 'ceiling':
                assert int(r['peak_nodes']) <= 5860
        if day in ('2022-03-07','2022-03-14'):
            week = '1' if day.endswith('-07') else '2'
            for new, prior in [('fifo_day','previous_day_fifo'),('ceiling','protected_ceiling'),
                               ('feasible_oracle','protected_feasible'),('protected_day','protected_previous_day')]:
                assert isclose(float(selections[new]['saved_all_kg']), float(old[week,prior]['saved_all_kg']), abs_tol=1e-7)
    # Perturb current and future estimates, job duration and the ordering of unrelated inputs.
    # A release-time signal may inspect only completed historical slots.
    t = epoch(date(2022,6,6))
    class PastOnly(dict):
        def get(self,k,default=None):
            assert k+STEP <= t
            return super().get(k,default)
    history = PastOnly(grid)
    for lags in ((1,), (7,), (7,14,21,28)):
        base = preferences([(t,3,10)],{0},history,lags)
        changed = PastOnly({k:(v if k<t else -999999) for k,v in grid.items()})
        assert base == preferences([(t,3,7*DAY)],{0},changed,lags)
    print('All included weeks: exact integrated baselines and upper bounds; both original March windows reproduced.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('cache', type=Path)
    audit(p.parse_args().cache)
