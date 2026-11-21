# Chronological ARCHER2 start-time replay

The analysis tests the gross effect of a previous-day carbon signal in a capacity-limited release-time queue. Its endpoint covers all jobs starting in each week, including carbon after the end of the week. All eligibility and start proposals are independent of eventual runtimes. Each week initializes carry-in from the real trace. The source file includes a two-hour drain sample, but postweek arrivals are not admitted.

## Reproduce

Python 3.12.14 standard library, tested on x86-64 Linux. From this directory:

```sh
python scripts/dispatch.py
python scripts/verify.py
python scripts/opportunity.py
python scripts/verify_opportunity.py
python scripts/benchmark.py
```

The deterministic output tables are outputs/replay.csv and outputs/daily.csv. Each daily total attributes the full job to its release day. The simulator evaluates every combination of week, hypothetical participation (25%, 50%, 100% of jobs with at most four nodes) and delay bound (30, 60 minutes). Cohorts are nested and selected only from release-time fields. For all-job percentage reductions the denominator is gross unshifted compute carbon of all jobs released during that week. The participant denominator includes all selected jobs, whether they moved or stayed. Prefix-sum carbon accounting and a separate signed occupancy sweep cross-check the most demanding scenarios.

scripts/benchmark.py times the actual warm in-memory candidate comparisons against immediate-start bookkeeping. It writes a new timing log on each execution. Its alternating pairs compare complete loops over identical input. When a readable package counter exists under /sys/class/powercap, the program also returns *package* microjoules; isolate the machine and lengthen trials on a real target before interpreting small differences. The distributed run has empty energy columns because this execution host exposed no such counter. Package-level metering does not establish total scheduler-service energy or the energy of fetching forecasts.

## Opportunity with perfect knowledge

The output table for the two weeks is outputs/opportunity.csv. It includes separate participant and nonparticipant changes, the all-job total, both denominators, peak nodes, average and maximum realized wait, and the count beyond one hour. Output masses are kilograms. In outputs/replay.csv masses are grams.

1. previous_day_fifo uses the observed grid intensity one day earlier. clairvoyant_fifo proposes each job's independently preferred start using its realized entire duration and future grid intensities. Both feed the same chronological dispatcher. A candidate request can be at most one hour later. A blocked job can wait longer; 60 do in the first week of clairvoyant_fifo.
2. All protected methods pin nonparticipants and carry-in to the original schedule. They admit starts exactly 0, 30 or 60 minutes after recorded start. protected_previous_day orders candidate shifts by the previous day's intensity decline multiplied by node count. protected_feasible orders them by exact integrated emissions saving. The same offline capacity repair must know occupied intervals for both, so the protected previous-day row is a diagnostic rather than a deployable online algorithm. Each starts from the original feasible allocation, tries jobs in descending preference gain and commits a shift only when its newly occupied time segment fits. Existing jobs vacate the earlier interval. If the complete first-choice schedule is already feasible, it is used directly.
3. protected_ceiling drops interactions and sums the largest nonnegative individual saving. It costs jobs separately, but the peak_nodes column reports the actual occupancy one would need to implement their combined choices. It is an upper bound on the protected three-start class. A feasible joint assignment gives a lower bound. Bound and feasible result coincide in week two. In week one the independent assignments exceed physical node capacity. A continuous-time optimum, the best possible unrestricted FIFO control and a nationwide or annual carbon bound are outside this calculation.

verify_opportunity.py derives the protected upper bounds and participant split independently by explicit half-hour segment integration. It also exactly enumerates all 243 possible assignments in 64 small constrained examples to check the implementation’s feasibility and bound directions. The feasible greedy rule only matched the exact optimum in 13 of those examples. Week-one optimality is not asserted. Numerical outputs can be regenerated with Python 3.10 or later using the standard library.

## Attribution and input terms

- inputs/week*/archer2_allocations.csv transforms **HPC System Usage Data** by Adrian Jackson and Ioannis Lamprakis, [release 1.0](https://doi.org/10.5281/zenodo.14284189), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Selected start, end and node count, converted timestamps to Unix seconds and excluded invalid, empty allocations. Allocation release windows and raw source hashes appear in references.md.
- inputs/week*/gb_intensity.csv and inputs/drain_intensity.csv transform the GB **Carbon Intensity API** from National Energy System Operator and project partners, under its [terms](https://carbonintensity.org.uk/) and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). These files flatten national half-hour records and convert dates to epochs. Only actual estimates enter this paper. The extra drain intervals cover all completions. Keep attribution with derivative tables.
- inputs/archer2_meter_calibration.csv consists of a count and summary quantiles computed from the [HPC-JEEP job-step energy dataset](https://doi.org/10.5281/zenodo.7128646), Andrew Turner and Alastair Basden (2022), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) per the upstream release metadata. The original archive is not included.
- Vedant Thaker's analysis code is MIT-licensed. Neither that license nor the carbon reductions confer permission to delay any specific job.
