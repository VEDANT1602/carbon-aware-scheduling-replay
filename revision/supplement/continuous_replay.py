"""Pair daily-reset and continuous-week reservations on the original period and mixed grid."""
import csv
from pathlib import Path

import numpy as np
from run import DAY, IDLE_WATT, intensity, read_trace, schedule


def replay_period(arrivals, capacity, lag, horizon):
    length = len(arrivals) + 24
    indices = np.arange(length)
    # Evaluate each day at the identical clock phase, including the draining period.
    # The modulo avoids floating tie-break changes when an exact daily cycle repeats.
    truth = intensity(indices % DAY, "mixed")
    forecast = intensity((indices % DAY) - 12*lag, "mixed")
    earliest = schedule(arrivals, capacity, horizon, "earliest", truth, forecast)
    carbon = schedule(arrivals, capacity, horizon, "carbon", truth, forecast)
    gross = earliest["job_g"] - carbon["job_g"]
    idle = IDLE_WATT * 300 * truth.sum() / 3600000
    return dict(jobs=carbon["jobs"], late=carbon["late"], earliest_late=earliest["late"],
                gross_g=gross, lookup_g=carbon["overhead_g"], net_g=gross-carbon["overhead_g"],
                g_per_j=carbon["g_per_lookup_j"], base_total_g=earliest["job_g"]+idle,
                delay_sum=carbon["delay_sum_min"])


def main():
    frame = read_trace()
    capacity = int(np.ceil(np.nanquantile(frame[:7], .95)))
    test = np.nan_to_num(frame[7:], nan=0).astype(int)
    summaries = []
    for mode, periods in (("daily_reset", test), ("continuous_week", [test.ravel()])):
        for lag in (0, 2, 6, 12):
            for horizon in (6, 12):
                periods_out = [replay_period(period, capacity, lag, horizon) for period in periods]
                totals = {k: sum(row[k] for row in periods_out) for k in periods_out[0]}
                summaries.append(dict(mode=mode, lag_h=lag, allowance_min=5*horizon, **totals,
                                      break_even_j_per_lookup=totals["gross_g"]/totals["g_per_j"],
                                      mean_delay_min=totals["delay_sum"]/totals["jobs"]))
    with Path(__file__).with_name("continuous_replay.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=summaries[0].keys())
        writer.writeheader()
        writer.writerows(summaries)

if __name__ == "__main__":
    main()
