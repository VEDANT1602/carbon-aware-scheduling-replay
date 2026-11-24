"""Stress-test the fixed four-week protected schedule with heterogeneous job power."""
import argparse
import csv
from datetime import date
from math import isclose
from pathlib import Path

from dispatch import ROOT, WEEK, load, queue_sim
from fetch_seasonal import ALLOCATION_URL, checksum
from opportunity import protected_schedule
from seasonal import GridAccount, LAGS, allocation_windows, epoch, grids, preferences, write_table


def read_output(filename):
    with (ROOT / "outputs" / filename).open(newline="") as stream:
        return list(csv.DictReader(stream))


def assess(cache):
    grid, sources = grids(cache)
    sources.append({"source": ALLOCATION_URL, "sha256": checksum(cache / "Archer2SummaryData.csv")})
    if {tuple(x.values()) for x in sources} != {tuple(x.values()) for x in read_output("seasonal_inputs.csv")}:
        raise ValueError("The downloaded inputs differ from the archived source digests.")
    windows = allocation_windows(cache)
    meter = load("archer2_meter_calibration.csv")[0]
    p25, median_power, p75 = [float(meter[k]) for k in ("q25_W_per_node", "median_W_per_node", "q75_W_per_node")]
    account = GridAccount(grid, median_power)
    results = []
    for reference in read_output("seasonal.csv"):
        if reference["method"] != "protected_four_weeks":
            continue
        day = reference["release_monday"]
        start = epoch(date.fromisoformat(day))
        rows = windows[start]
        jobs, starts, _, _ = queue_sim(rows, start, start + WEEK, (0,), 0, grid, start // WEEK)
        opted = {i for i, (_, nodes, _) in enumerate(jobs) if nodes <= 4}
        gains, targets, _ = preferences(jobs, opted, grid, LAGS["four_weeks"])
        carry = [(end, nodes) for t, end, nodes in rows if t < start < end]
        proposed = dict(starts)
        proposed.update(targets)
        shifted = protected_schedule(jobs, carry, start, gains, proposed)
        saving = [account.kg(t, nodes, duration) - account.kg(shifted[i], nodes, duration)
                  for i, (t, nodes, duration) in enumerate(jobs)]
        positive = sum(x for x in saving if x > 0)
        negative = sum(x for x in saving if x < 0)
        total = positive + negative
        if not isclose(total, float(reference["saved_all_kg"]), abs_tol=1e-7):
            raise ValueError(f"Reconstructed schedule misses the archived carbon total for {day}.")
        # Each job keeps the same power across both alternatives. The carbon change is linear in that power.
        low = (p25 * positive + p75 * negative) / median_power
        high = (p75 * positive + p25 * negative) / median_power
        results.append(dict(release_monday=day, jobs=len(jobs), positive_kg=positive, negative_kg=negative,
                            uniform_median_kg=total, minimum_scenario_kg=low, maximum_scenario_kg=high))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cache", type=Path)
    args = parser.parse_args()
    write_table(ROOT / "outputs" / "power_sensitivity.csv", assess(args.cache))
