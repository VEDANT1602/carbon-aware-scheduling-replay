"""Check the workload counts, queue metrics and published break-even accounting."""
import csv
import hashlib
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent


def near(label, observed, expected, tolerance=.00501):
    if not math.isclose(observed, expected, rel_tol=0, abs_tol=tolerance):
        raise ValueError(f"{label}: observed {observed}, expected {expected}")


def workload_totals():
    path = ROOT / "elb_request_count_8c0756.csv"
    data = path.read_bytes().replace(b"\r\n", b"\n")
    git_digest = hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if git_digest != "c2c83f9f470653d5db71f8aa6a038a98e075c7ae":
        raise ValueError("Input count series differs from the upstream Git object")
    daily = defaultdict(int)
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            timestamp = datetime.fromisoformat(row["timestamp"])
            if datetime(2014,4,17) <= timestamp < datetime(2014,4,24):
                daily[timestamp.day] += int(float(row["value"]))
    if sum(daily.values()) != 117154 or len(daily) != 7:
        raise ValueError("Unexpected evaluation-day counts")
    return daily


def main():
    daily = workload_totals()
    with (ROOT / "results.csv").open(encoding="utf-8", newline="") as stream:
        records = list(csv.DictReader(stream))
    dimensions = ("fill","day","grid","phase_h","horizon_min","policy")
    if len(records) != 1008 or len({tuple(row[k] for k in dimensions) for row in records}) != 1008:
        raise ValueError("Missing or duplicate scenario rows")
    for row in records:
        parts = sum(float(row[k]) for k in ("job_g","overhead_g","idle_g"))
        near("component sum", parts, float(row["total_g"]), 1e-8)
        if row["fill"] == "zero" and int(row["jobs"]) != daily[int(row["day"])]:
            raise ValueError("Observed arrivals were not conserved")
    def selected(policy, lag):
        return [r for r in records if r["fill"]=="zero" and r["grid"]=="mixed" and r["horizon_min"]=="60"
                and r["policy"]==policy and int(r["phase_h"])==lag]
    def total(rows, field):
        return math.fsum(float(r[field]) for r in rows)
    base, aligned, lagged = selected("earliest",0), selected("carbon",0), selected("carbon",2)
    if any(len(group)!=7 for group in (base,aligned,lagged)):
        raise ValueError("Expected seven matched evaluation days")
    gross = total(base,"job_g")-total(aligned,"job_g")
    net = total(base,"total_g")-total(aligned,"total_g")
    penalty = total(lagged,"total_g") - total(selected("earliest",2),"total_g")
    threshold = gross/total(aligned,"g_per_lookup_j")
    near("baseline work grams",total(base,"job_g"),458.00)
    near("forecast work grams",total(aligned,"job_g"),424.08)
    near("baseline total grams",total(base,"total_g"),1208.22)
    near("forecast total grams",total(aligned,"total_g"),1180.12)
    near("forecast lookup grams",total(aligned,"overhead_g"),5.81)
    near("lookup count",total(aligned,"lookups"),26169,0)
    near("work saving",gross,33.91)
    near("net saving",net,28.10)
    near("net saving percent",100*net/total(base,"total_g"),2.33)
    near("two-hour lag penalty",penalty,36.75)
    near("joules per lookup",threshold,11.67)
    for group,p95 in ((base,0),(aligned,60)):
        near("median daily p95",median(int(r["p95_min"]) for r in group),p95,0)
        near("late jobs",total(group,"late"),0,0)
    print(f"Verified 1,008 daily scenarios and {sum(daily.values()):,} main-analysis jobs.")
    print(f"Aligned net saving {net:.2f} g CO2e; break-even {threshold:.2f} J/lookup.")
    print(f"Two-hour lag increases modeled emissions by {penalty:.2f} g CO2e.")


if __name__ == "__main__":
    main()
