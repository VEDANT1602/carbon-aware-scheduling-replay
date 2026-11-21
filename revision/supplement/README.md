# Forecast lookup costs | reproduction and continuous-week replay

## Original experiment

Original version: https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/dea2cea99bfc52fb21a7321fdc0d676060e5472d . The included run.py, verify.py, requirements.txt, CITATION.cff, results.csv, input CSV and NAB-LICENSE come from that commit. NAB-LICENSE is the upstream data notice. The original study repository names Vedant Thaker as software author and contains no separate project-wide code license at this commit.

Use Python 3.11 and `python -m pip install -r requirements.txt` for the declared NumPy 1.26.0 environment. From this directory:

1. Run `python verify.py` to check the distributed results and the workload identity.
2. Make a copy of results.csv named distributed.csv for comparison.
3. Run `python run.py` to regenerate results.csv, followed by `python verify.py`.
4. Run `python compare_results.py distributed.csv results.csv` to compare every field keyed by day and configuration. The revision rerun used Python 3.12.14 and NumPy 2.3.5. All integer fields and identifiers agreed. Floating serialization differed in 158 rows, with largest absolute numeric difference 5.69e-14 or smaller.

The 1,008 rows comprise 7 days × 2 missing-value conventions × 3 grid curves × 4 forecast lags × 3 deadlines × 2 policies. The raw count series has Git blob c2c83f9f470653d5db71f8aa6a038a98e075c7ae.

## Revision analysis

Run `python continuous_replay.py` to regenerate continuous_replay.csv. The 16 rows cross daily/weekly queue boundaries, forecast lags of 0, 2, 6 and 12 hours, and deadlines of 30 or 60 minutes. Both modes use the same training-derived capacity, zero-imputed arrivals, clock-aligned mixed grid and modeled energy parameters. The 26-hour daily replay includes two hours of idle drain each day. The continuous week includes one two-hour idle drain at its end.

Positive net_g means forecast scheduling produces fewer modeled grams of CO2e. Negative break_even_j_per_lookup means a free forecast would already lose carbon. The jobs column counts hypothetical deferrable work units; the observations are AWS load-balancer counts. No energy was metered. The two revision scripts and their outputs are supplied with the manuscript package separately from the pinned public archive.

## Environment lock

Create separate Linux x86_64 virtual environments with CPython 3.12.14 for the revision and 3.11.9 for the baseline. In the activated revision environment run `python -m pip install --require-hashes -r revision-cp312-linux-x86_64.lock`. For the original checkout, install `baseline-cp311-linux-x86_64.lock` the same way in the baseline environment, then run the commands above. The 3.11 baseline lock pins NumPy 1.26.0; the 3.12 revision lock pins NumPy 2.3.5 for the revised replay and its reported numeric comparison. The lock headers identify the platform; the baseline transitive pins reconstruct a compatible environment for the published direct requirements.

## Dated allocations, metering and the real grid

1. Run `python dated_replay.py` and `python check_dated.py` for March 7–13, 2022 UTC. Rerun each command with `--repeat` for March 14–20. Only Python's standard library is required. `dated_results.csv` contains the counterfactual weekly pricing calculations, `dated_daily.csv` retains seven paired daily values, and `primary_start_choices.csv` logs the independent capacity/energy check. Each row in the derived input trace is an observed node allocation with its original start, finish and node count.
2. To reconstruct the inputs from the official releases, download the two Zenodo files, the Grid Workloads Archive SQLite zip, and the NESO interval response listed in DATA-SOURCES.md. Run `python extract_observations.py Archer2SummaryData.csv HPC-JEEP_WP1_data.tar.gz gwa_t_2_anon_jobs_sqlite.zip neso.json`. Repeat with the later NESO range and `--repeat`. Monthly hardware-power quantiles weight valid recorded steps equally. Raw files with job names or account identifiers are not redistributed.
3. The primary decision signal uses the previous day's GB profile. The archived forecast and perfect hindsight are retrospective sensitivity checks. No per-job user deadline or forecast-service energy meter is inferred from timestamps. Slacks alter permissible start times only in the counterfactual. Fixed French reservations are analyzed separately in reservation_audit.csv.
