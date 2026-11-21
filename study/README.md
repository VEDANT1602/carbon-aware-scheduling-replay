# Chronological ARCHER2 start-time replay

The analysis tests the gross effect of a previous-day carbon signal in a capacity-limited release-time queue. Its endpoint covers all jobs starting in each week, including carbon after the end of the week. All eligibility and start proposals are independent of eventual runtimes. Each week initializes carry-in from the real trace. The source file includes a two-hour drain sample, but postweek arrivals are not admitted.

## Reproduce

Python 3.12.14 standard library, tested on x86-64 Linux. From this directory:

```sh
python scripts/dispatch.py
python scripts/verify.py
python scripts/benchmark.py
```

The deterministic output tables are outputs/replay.csv and outputs/daily.csv. Each daily total attributes the full job to its release day. The simulator evaluates every combination of week, hypothetical participation (25%, 50%, 100% of jobs with at most four nodes) and delay bound (30, 60 minutes). Cohorts are nested and selected only from release-time fields. For all-job percentage reductions the denominator is gross unshifted compute carbon of all jobs released during that week. The participant denominator includes all selected jobs, whether they moved or stayed. Prefix-sum carbon accounting and a separate signed occupancy sweep cross-check the most demanding scenarios.

scripts/benchmark.py times the actual warm in-memory candidate comparisons against immediate-start bookkeeping. It writes a new timing log on each execution. Its alternating pairs compare complete loops over identical input. When a readable package counter exists under /sys/class/powercap, the program also returns *package* microjoules; isolate the machine and lengthen trials on a real target before interpreting small differences. The distributed run has empty energy columns because this execution host exposed no such counter. Package-level metering does not establish total scheduler-service energy or the energy of fetching forecasts.

## Attribution and input terms

- inputs/week*/archer2_allocations.csv transforms **HPC System Usage Data** by Adrian Jackson and Ioannis Lamprakis, [release 1.0](https://doi.org/10.5281/zenodo.14284189), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Selected start, end and node count, converted timestamps to Unix seconds and excluded invalid, empty allocations. Allocation release windows and raw source hashes appear in references.md.
- inputs/week*/gb_intensity.csv and inputs/drain_intensity.csv transform the GB **Carbon Intensity API** from National Energy System Operator and project partners, under its [terms](https://carbonintensity.org.uk/) and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). These files flatten national half-hour records and convert dates to epochs. Only actual estimates enter this paper. The extra drain intervals cover all completions. Keep attribution with derivative tables.
- inputs/archer2_meter_calibration.csv consists of a count and summary quantiles computed from the [HPC-JEEP job-step energy dataset](https://doi.org/10.5281/zenodo.7128646), Andrew Turner and Alastair Basden (2022), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) per the upstream release metadata. The original archive is not included.
- Vedant Thaker's analysis code is MIT-licensed. Neither that license nor the carbon reductions confer permission to delay any specific job.
