"""Reproduce request-count replay. Python 3.11 and NumPy 1.26.

Input: Numenta/NAB data/realAWSCloudwatch/elb_request_count_8c0756.csv.
Run python run.py from any directory. No network required.
"""
import csv
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DAY = 288
GRID = {"flat": (0,0), "diurnal": (150,0), "mixed": (150,65)}
E_JOB, E_LOOK, IDLE_WATT = 36., 2., 10.


def read_trace():
    frame = np.full((14, DAY), np.nan)
    origin = datetime(2014,4,10,0,4)
    with (HERE / "elb_request_count_8c0756.csv").open() as f:
        for row in csv.DictReader(f):
            elapsed = (datetime.fromisoformat(row["timestamp"])-origin).total_seconds()
            assert elapsed >= 0 and elapsed % 300 == 0
            day, slot = divmod(int(elapsed // 300), DAY)
            if day < 14:
                value = float(row["value"])
                assert np.isnan(frame[day,slot]) and value.is_integer() and value >= 0
                frame[day,slot] = value
    return frame


def intensity(indices, kind):
    daily, fast = GRID[kind]
    return 400 + daily*np.cos(2*np.pi*(indices-36)/DAY) + fast*np.cos(2*np.pi*(indices-6)/48)


def schedule(arrivals, capacity, horizon, policy, actual, forecast):
    booked = np.zeros(len(actual), dtype=int)
    delays = np.zeros(len(actual), dtype=int)
    lookups = np.zeros(len(actual), dtype=int)
    for t, demand in enumerate(arrivals):
        if demand == 0:
            continue
        choices = list(range(t,t+horizon+1))
        if policy == "carbon":
            lookups[t] = len(choices)
            choices.sort(key=lambda s: (forecast[s], s))
        for s in choices:
            count = min(demand, capacity - booked[s])
            booked[s] += count
            delays[s-t] += count
            demand -= count
            if demand == 0:
                break
        s = t+horizon+1
        while demand > 0:
            count = min(demand, capacity - booked[s])
            booked[s] += count
            delays[s-t] += count
            demand -= count
            s += 1
    total = sum(arrivals)
    assert booked.sum() == delays.sum() == total
    assert booked.max() <= capacity
    work_g = np.dot(booked,actual)*E_JOB/3600000
    overhead_per_j = np.dot(lookups,actual)/3600000
    return dict(jobs=int(total), p95_min=int(5*np.searchsorted(delays.cumsum(), .95*total)),
                late=int(delays[horizon+1:].sum()), delay_sum_min=int(5*np.dot(delays,np.arange(len(delays)))),
                job_g=work_g, lookups=int(lookups.sum()), overhead_g=overhead_per_j*E_LOOK,
                g_per_lookup_j=overhead_per_j)


def main():
    frame = read_trace()
    capacity = int(np.ceil(np.nanquantile(frame[:7], .95)))
    fill = int(np.nanmedian(frame[:7]))
    print("training q95 capacity", capacity, "training median", fill, "missing per day", np.isnan(frame).sum(1))
    rows = []
    for impute in ("zero","train_median"):
        test = np.nan_to_num(frame[7:], nan=0 if impute=="zero" else fill).astype(int)
        for day, arrivals in enumerate(test):
            # A fixed meter window includes a conservative drain period even for empty slots.
            length = DAY + 24
            indices = np.arange(length)
            for kind in GRID:
                truth = intensity(indices, kind)
                idle_g = IDLE_WATT*300*truth.sum()/3600000
                for phase_hours in (0,2,6,12):
                    forecast = intensity(indices-12*phase_hours, kind)
                    for horizon in (0,6,12):
                        for policy in ("earliest","carbon"):
                            m = schedule(arrivals, capacity, horizon, policy, truth, forecast)
                            rows.append(dict(fill=impute, day=day+17, grid=kind, phase_h=phase_hours, horizon_min=horizon*5,
                                             policy=policy, capacity=capacity, **m, idle_g=idle_g,
                                             total_g=m["job_g"]+idle_g+m["overhead_g"]))
    with (HERE / "results.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    for phase in (0,2,6,12):
        for horizon in (0,30,60):
            sub = [r for r in rows if r["fill"]=="zero" and r["grid"]=="mixed" and r["phase_h"]==phase and r["horizon_min"]==horizon]
            base = [r for r in sub if r["policy"]=="earliest"]
            carbon = [r for r in sub if r["policy"]=="carbon"]
            def total(rr, col): return sum(r[col] for r in rr)
            gross = total(base,"job_g") - total(carbon,"job_g")
            net = total(base,"total_g") - total(carbon,"total_g")
            print(phase,horizon, "total jobs, base late, carbon late, median daily p95 base/green, gross/net g, net %, break-even joules",
                  total(base,"jobs"),total(base,"late"),total(carbon,"late"),np.median([r["p95_min"] for r in base]),
                  np.median([r["p95_min"] for r in carbon]),round(gross,3),round(net,3),round(100*net/total(base,"total_g"),3),
                  round(gross/total(carbon,"g_per_lookup_j"),3))


if __name__ == "__main__":
    main()
