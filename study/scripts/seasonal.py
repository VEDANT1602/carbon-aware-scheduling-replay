"""Matched weekly ARCHER2 comparisons using only past national intensities for forecasts."""
import argparse
import csv
import json
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from math import ceil, isclose
from pathlib import Path
from statistics import mean

from dispatch import CAPACITY, ROOT, STEP, WEEK, load, queue_sim
from fetch_seasonal import ALLOCATION_SHA256, ALLOCATION_URL, checksum, grid_windows
from opportunity import OFFSETS, census, protected_schedule

DAY = 86400
LAGS = {'day': (1,), 'week': (7,), 'four_weeks': (7, 14, 21, 28)}


def epoch(day):
    return int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())


def release_weeks():
    mondays = []
    for month in range(1, 10):
        first = date(2022, month, 1)
        mondays.append(first + timedelta(days=(-first.weekday()) % 7))
    return sorted(mondays + [date(2022, 3, 14)])


def grids(cache):
    grid = {}
    manifest = []
    for url, name in grid_windows():
        path = cache / name
        for rec in json.loads(path.read_text())['data']:
            slot = int(datetime.fromisoformat(rec['from'].replace('Z', '+00:00')).timestamp())
            value = rec['intensity']['actual']
            if slot in grid and grid[slot] != value:
                raise ValueError(f'Inconsistent source estimates at {slot}')
            grid[slot] = value
        manifest.append({'source': url, 'sha256': checksum(path)})
    return grid, manifest


def allocation_windows(cache):
    path = cache / 'Archer2SummaryData.csv'
    assert checksum(path) == ALLOCATION_SHA256
    starts = [epoch(day) for day in release_weeks()]
    windows = {s: [] for s in starts}
    with path.open(newline='') as stream:
        for row in csv.DictReader(stream):
            try:
                s, e, n = int(row['Start']), int(float(row['End'])), int(row['AllocNodes'])
            except (ValueError, OverflowError):
                continue
            if e <= s or n <= 0:
                continue
            for start in starts:
                if e > start and s < start + WEEK:
                    windows[start].append((s, e, n))
    for rows in windows.values():
        rows.sort(key=lambda j: (j[0], j[2]))
    return windows


class GridAccount:
    """Integrate piecewise-constant estimates and fail if any required slot is missing."""
    def __init__(self, grid, watts):
        self.origin = min(grid)
        self.watts = watts
        self.values = [grid.get(t) for t in range(self.origin, max(grid) + STEP, STEP)]
        self.sums = [0]
        self.missing = [0]
        for value in self.values:
            self.sums.append(self.sums[-1] + (value or 0) * STEP)
            self.missing.append(self.missing[-1] + (value is None))

    def integral(self, t):
        i, r = divmod(t - self.origin, STEP)
        return self.sums[i] + (r * self.values[i] if r else 0)

    def kg(self, t, n, d):
        left = (t - self.origin) // STEP
        right = ceil((t + d - self.origin) / STEP)
        if left < 0 or right > len(self.values) or self.missing[right] != self.missing[left]:
            raise ValueError('Missing outcome intensity in a billed interval')
        return n * self.watts * (self.integral(t + d) - self.integral(t)) / 3.6e9


def preferences(jobs, opted, grid, lags):
    @lru_cache(maxsize=None)
    def signal(slot):
        patterns = []
        for lag in lags:
            reference = slot - lag * DAY
            # Every sampled half hour has ended by release, including the last proposed offset.
            assert reference + max(OFFSETS) + STEP <= slot
            samples = tuple(grid.get(reference + k) for k in OFFSETS)
            if all(x is not None for x in samples):
                patterns.append(samples)
        return tuple(mean(col) for col in zip(*patterns)) if patterns else ()

    gains, targets, unavailable = {}, {}, 0
    for i in opted:
        s, n, _ = jobs[i]
        pred = signal((s // STEP) * STEP)
        if not pred:
            unavailable += 1
        gains[i] = {k: n * (pred[0] - pred[j]) if pred else 0 for j, k in enumerate(OFFSETS)}
        targets[i] = s + max(OFFSETS, key=lambda k: (gains[i][k], -k))
    return gains, targets, unavailable


def compare(start, rows, grid, account):
    week = start // WEEK
    jobs, initial_times, _, _ = queue_sim(rows, start, start + WEEK, (0,), 0, grid, week)
    opted = {i for i, (_, nodes, _) in enumerate(jobs) if nodes <= 4}
    assert jobs and all(initial_times[i] == s for i, (s, n, d) in enumerate(jobs))
    carry = [(e, n) for s, e, n in rows if s < start < e]
    initial = [account.kg(s, n, d) for s, n, d in jobs]
    baseline = sum(initial)
    part_baseline = sum(initial[i] for i in opted)
    gains = {i: {k: initial[i] - account.kg(s + k, n, d) for k in OFFSETS}
             for i, (s, n, d) in enumerate(jobs) if i in opted}
    best = {i: jobs[i][0] + max(OFFSETS, key=lambda k: (g[k], -k)) for i, g in gains.items()}
    ceiling_times = initial_times.copy()
    ceiling_times.update(best)
    feasible = protected_schedule(jobs, carry, start, gains, ceiling_times)
    methods = [('ceiling', ceiling_times, 0), ('feasible_oracle', feasible, 0)]
    for name, lags in LAGS.items():
        forecast, targets, no_signal = preferences(jobs, opted, grid, lags)
        _, timing, _, _ = queue_sim(rows, start, start + WEEK, OFFSETS, 100, grid, week, offline_targets=targets)
        requested = initial_times.copy()
        requested.update(targets)
        fixed = protected_schedule(jobs, carry, start, forecast, requested)
        methods += [('fifo_' + name, timing, no_signal), ('protected_' + name, fixed, no_signal)]
    out = []
    for name, timetable, no_signal in methods:
        changes = [old - account.kg(timetable[i], n, d) for i, ((s, n, d), old) in enumerate(zip(jobs, initial))]
        part = sum(changes[i] for i in opted); gross = sum(changes)
        delta = [timetable[i] - s for i, (s, n, d) in enumerate(jobs)]
        peak = census(jobs, timetable, carry, start)
        if name != 'ceiling':
            assert peak <= CAPACITY
        if not name.startswith('fifo_'):
            assert all(d in OFFSETS for d in delta) and all(d == 0 for i,d in enumerate(delta) if i not in opted)
        out.append(dict(release_monday=datetime.fromtimestamp(start, timezone.utc).date().isoformat(),
                        method=name, jobs=len(jobs), participants=len(opted), no_signal_participants=no_signal,
                        all_baseline_kg=baseline, participant_baseline_kg=part_baseline,
                        saved_all_kg=gross, saved_participant_kg=part, saved_nonparticipant_kg=gross-part,
                        saved_all_pct=100*gross/baseline, saved_participant_pct=100*part/part_baseline,
                        mean_delay_min=mean(delta)/60, peak_nodes=peak))
    assert isclose(out[0]['saved_all_kg'], sum(max(v.values()) for v in gains.values()), abs_tol=1e-7)
    assert all(r['saved_all_kg']<=out[0]['saved_all_kg']+1e-7 for r in out if not r['method'].startswith('fifo_'))
    return out


def write_table(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(cache):
    grid, manifest = grids(cache)
    manifest.insert(0, {'source': ALLOCATION_URL, 'sha256': ALLOCATION_SHA256})
    write_table(ROOT / 'outputs' / 'seasonal_inputs.csv', manifest)
    windows = allocation_windows(cache)
    account = GridAccount(grid, float(load('archer2_meter_calibration.csv')[0]['median_W_per_node']))
    all_rows = []
    status = []
    for start, rows in windows.items():
        day = datetime.fromtimestamp(start, timezone.utc).date().isoformat()
        releases = [r for r in rows if start<=r[0]<start+WEEK]
        jobs = [(s,n,e-s) for s,e,n in releases]
        raw_peak = census(jobs, {i:j[0] for i,j in enumerate(jobs)},
                          [(e,n) for s,e,n in rows if s<start], start)
        disposition = dict(release_monday=day, releases=len(releases), source_peak_nodes=raw_peak)
        if raw_peak > CAPACITY:
            status.append(dict(**disposition, status='recorded demand exceeds installed capacity'))
            continue
        try:
            result = compare(start, rows, grid, account)
        except ValueError as error:
            if str(error) != 'Missing outcome intensity in a billed interval':
                raise
            status.append(dict(**disposition, status=str(error)))
            continue
        status.append(dict(**disposition, status='complete'))
        all_rows.extend(result)
        print(day, len(releases), flush=True)
    write_table(ROOT / 'outputs' / 'seasonal.csv', all_rows)
    write_table(ROOT / 'outputs' / 'seasonal_windows.csv', status)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cache',type=Path)
    run(parser.parse_args().cache)
