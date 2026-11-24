# The carbon opportunity in one hour of flexibility at ARCHER2

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

Scheduling study · November 24, 2026

### Abstract

ARCHER2 publishes job starts but records neither submission times nor permission to defer jobs in this dataset. We use its observed starts to ask a narrower question: how much national-average compute carbon could three start choices have changed? Eight weeks from March through September 2022 cover 292,776 allocations. For jobs with up to four nodes we allowed delays of zero, 30 or 60 minutes and kept other starts fixed. A four-week same-weekday signal yielded a modeled saving of 204.23 kg CO₂ (0.0313% of all-job compute emissions), against 116.09 kg for the previous-day signal. Letting each job draw a fixed power within the central half of the March meter distribution gave a pooled four-week-signal saving of 101–289 kg across extreme assignments. A feasible schedule with perfect information saved 1,001.99 kg. Relaxing capacity raised the upper bound to 1,017.09 kg (0.1559%). This bounds the opportunity within the assumed start choices and constant-power account.

## The decision and the sample

A scheduler considering two later starts must estimate when the grid will be cleaner. Even an accurate forecast has little value if few jobs can move or the signal barely changes across those starts. Forecast-informed capacity controls are used in production [1], and comparisons across cloud workloads show that attainable reductions vary with the trace and location [2]. Here the question is how much of the available saving three simple signals can capture on the same calendar.

The allocation archive gives UTC starts, ends and node counts [4]. We selected the first Monday-starting week of each calendar month from January to September 2022. We also retained March 14–20 to compare with the adjacent March week. Each week is a separate replay. All jobs starting in the week enter the carbon account through their completion. Already running jobs retain their original finish and occupy capacity. The resulting eight weeks cover seven months at one site. March contributes two weeks. A pooled total weights weeks by baseline emissions.

Two candidate weeks failed the feasibility check before policy scoring. Taken literally, their recorded concurrent allocations require 6,621 nodes in the week starting January 3 and 5,865 in the week starting February 7. Installed capacity is 5,860 nodes [8]. We excluded both whole weeks, retained the date and peak in the supplement, and did not select replacements. The cause of the discrepancy is unknown. In each included week an immediate-start replay recovered every recorded release-cohort start.

## Three signals, one set of start choices

The recorded start acts as the release. Jobs with one to four nodes may request an immediate start or a delay of 30 or 60 minutes; larger jobs cannot request a change. For each candidate, the policy scores the half hour containing its start under one of three rules. **Day** uses that UTC slot yesterday. **Week** uses it seven days ago. **Four weeks** averages the values 7, 14, 21 and 28 days earlier. Each lag contributes only if values for all three candidate slots exist. The earliest start wins a tie. The no-history fallback is an immediate start; no participant in these eight weeks needed it. Each input half hour had ended before the job’s recorded start. The archive supplies realized grid-intensity estimates without their initial publication times or past vintages [7]. These three signals are historical persistence rules. A production forecast comparison would require the values that were actually available at each decision time. UTC defines the seasonal cycle even at the daylight-saving transition.

We evaluate each signal under two service rules. Under the **forward queue**, requests enter a first-in, first-out ready queue and start when nodes become available. This decision needs only the release, the node count, the signal and observed completions. Incidental blocking can delay larger jobs or extend a participant’s wait past one hour. Under **protected starts**, larger jobs keep their original starts, and small jobs must use exactly one of the three allowed offsets. If the first-choice schedule exceeds capacity, an offline procedure considers shifts in descending order of the signal’s estimated intensity drop multiplied by node count. It accepts a shift only if the occupied intervals fit. The protected calculation therefore uses the original occupancy timetable to enforce the contract.

The **oracle** evaluates each participant’s full run at all three starts against the realized grid series. Summing the best individual savings ignores contention and bounds the protected schedule from above. Scheduling candidate shifts in descending order of these savings, subject to capacity, supplies a feasible lower bound on the optimum. Carry-in jobs never move. Both bounds use the same jobs, power model and allowed starts as the protected signals.

## Savings across the eight weeks

The account integrates national half-hourly intensity [7] over each run and multiplies it by allocated nodes and 512.18 W/node. That common power is the median of 953,798 positive ARCHER2 job-step readings from March out of 966,839 completed steps; the interquartile range was 438.18–541.10 W/node [5,6]. These meter records cannot be joined to the individual allocations. A common power changes the mass scale equally under every policy. It does not capture job-specific power or changes in the job mix over the year.

| Week starting (2022, UTC) | All jobs | Day (%) | Week (%) | Four weeks (%) | Oracle ceiling (%) |
|---|---:|---:|---:|---:|---:|
| 03-07 | 38,794 | 0.0922 | 0.1251 | 0.1305 | 0.4061 |
| 03-14 | 37,971 | 0.0233 | 0.0540 | 0.0540 | 0.2258 |
| 04-04 | 29,057 | 0.0259 | 0.0276 | 0.0354 | 0.1727 |
| 05-02 | 24,461 | 0.0202 | 0.0136 | 0.0149 | 0.0668 |
| 06-06 | 54,952 | 0.0156 | 0.0357 | 0.0576 | 0.1601 |
| 07-04 | 43,989 | −0.0280 | −0.0009 | −0.0016 | 0.1026 |
| 08-01 | 32,932 | 0.0185 | 0.0035 | 0.0113 | 0.1754 |
| 09-05 | 30,620 | 0.0060 | 0.0102 | 0.0038 | 0.0788 |
| **Pooled** | **292,776** | **0.0178** | **0.0276** | **0.0313** | **0.1559** |

Table 1. Gross saving with protected starts as a percentage of all jobs’ baseline compute emissions. Negative values mean more emissions. The pooled denominator is 652,487.47 kg CO₂. Of all releases, 241,030 were small enough to participate.

Four-week persistence captured 20.1% of the pooled ceiling; day and week persistence captured 11.4% and 17.7%. The extra historical weeks improved on yesterday in both March cohorts and in June. In May and August the day rule performed best of the three; in September single-week persistence performed best. All three protected rules increased emissions in July despite a positive oracle ceiling. The low July savings are therefore not explained solely by a lack of flexible starts. Eight selected weeks do not establish a recurring seasonal ranking.

| Selection of starts | Saved CO₂ with protected starts (kg) | Saved CO₂ in forward queue (kg) | Mean added wait in forward queue (min) |
|---|---:|---:|---:|
| Day persistence | 116.09 | 121.48 | 23.13 |
| Week persistence | 180.23 | 182.64 | 23.65 |
| Four-week mean | 204.23 | 210.76 | 24.56 |
| Feasible protected oracle | 1,001.99 | — | — |
| Protected oracle ceiling | 1,017.09 | — | — |

Table 2. Pooled masses and job-weighted mean waits. The feasible and capacity-relaxed schedules bound the best possible protected saving between 0.1536% and 0.1559%. The forward queue allows incidental delays outside that contract.

For March 7 and 14, the protected day signal reached 22.7% and 10.3% of ceilings of 221.58 and 167.62 kg. In the second March week the forward queue cut participant emissions by 17.86 kg (0.1144% of participant baseline). Five delayed nonparticipants added 0.03 kg, leaving 17.83 kg of modeled saving (0.0240% of all-job baseline).

## Sensitivity to job power

The meter distribution allows a stress test of the pooled result even though it cannot identify any job’s actual power. We held the four-week protected schedule fixed. At the median 512.18 W/node, the jobs that moved to cleaner intervals saved 571.12 kg, while those that moved to dirtier intervals added 366.89 kg. Each job’s carbon change scales linearly with its power if the job draws the same power at either start.

Assign each job a constant power in the interval 438.18–541.10 W/node, the March meter quartiles. Aggregate saving is smallest when every carbon-saving job draws the lower power and every carbon-increasing job draws the upper power. Interchanging the assignments gives the largest saving. Across the eight cohorts the resulting range was 100.99–289.49 kg, compared with 204.23 kg at the common median. For July it extended from an increase of 10.82 kg to a saving of 8.16 kg. Power heterogeneity within this interval therefore preserves the sign of the pooled saving but can change the sign for July. The interval covers only the middle half of the March step-level meter distribution. Actual job powers outside it, time-varying draw within jobs and correlation with workload remain unmeasured.

## Interpretation

Changing from yesterday’s signal to a four-week mean captured an additional 88.14 kg across the protected sample. Much more apparent potential separates that forecast from the oracle. The oracle knows future intensity and each runtime, while the three forecasts score only the starting half hour. Their distance to the oracle combines errors in the grid signal with the value of knowing how long jobs will run. The best feasible saving is still small relative to all modeled compute emissions.

Feng et al. [3, §IV-A and Table III] estimated a 15.4% reduction at 1.5 hours of additional mean waiting on 157 held-out windows. Their 224 daily windows contained 165,887 filtered CEA-Curie jobs with recorded submission times. They randomly aligned the 2011 workloads with 2025 British grid intensity, assigned deadlines and assumed 10 W/core. Their earliest-feasible baseline and flexibility contract differ from the recorded-start account here.

This replay has no observed submission times, delay permissions, reservations or service priorities. It cannot reconstruct the production submission queue. The dates sample a fraction of one operating year; capacity conflicts remove two winter weeks. The account measures a change in attributed compute carbon using half-hourly national averages. Marginal grid emissions, facility loads and scheduler energy are outside its boundary, so the estimates cannot establish an electricity or site-level emissions saving. The small estimated benefit and the added waiting would need to be assessed together with users and the site operator before a deployment decision.

## Data and code availability

The supplement contains source URLs and checksums, weekly inclusion decisions, the eight-week policy table, the original March inputs and the independent integration checks. Retrieval scripts rebuild the extended analysis from the public ARCHER2 allocation file [4] and the British intensity archive [7]. Licensing and calibration sources accompany the scripts.

The bundled study directory includes the eight-week ledger, the per-week power sensitivity, the input manifest and the reproduction commands in its README. The public project is <https://github.com/VEDANT1602/carbon-aware-scheduling-replay>.

## Author and disclosures

Vedant Thaker is the sole author. He specified the comparison of forecast quality with scheduling flexibility and requested the cross-month test of seasonal persistence. OpenAI Codex assisted with the replay, seasonal and oracle calculations, the job-power sensitivity calculation, numerical and source checks, and drafting.

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The author declares no competing interests.

## References

[1] A. Radovanović et al. Carbon-Aware Computing for Datacenters. IEEE Transactions on Power Systems 38, 1270–1280 (2023). <https://doi.org/10.1109/TPWRS.2022.3173250>

[2] T. Sukprasert, A. Souza, N. Bashir, D. Irwin and P. Shenoy. On the Limitations of Carbon-Aware Temporal and Spatial Workload Shifting in the Cloud. EuroSys, 924–941 (2024). <https://doi.org/10.1145/3627703.3650079>

[3] W. Feng, A. Dasgupta, Z. D. Tekler, S. Ahuja, J. Zheng and X. Jiang. COAST: Congestion-Aware Start-Time Recommendations for Carbon-Aware HPC Jobs. arXiv:2609.05443v1 (2026), preprint. <https://arxiv.org/abs/2609.05443v1>

[4] A. Jackson and I. Lamprakis. HPC System Usage Data, v1.0. ARCHER2 Slurm summary dataset (2024). <https://doi.org/10.5281/zenodo.14284189>

[5] A. Turner and A. Basden. HPC-JEEP: Energy Usage on ARCHER2 and the DiRAC COSMA HPC services dataset (2022). <https://doi.org/10.5281/zenodo.7128646>

[6] A. Turner and A. Basden. HPC-JEEP: Energy Usage on ARCHER2 and the DiRAC COSMA HPC services. Technical report (2022). <https://doi.org/10.5281/zenodo.7137390>

[7] National Energy System Operator and partners. Carbon Intensity API for Great Britain. National half-hourly estimates and data license. <https://carbonintensity.org.uk/>

[8] ARCHER2 Service. Hardware overview. HPE Cray EX compute nodes and system configuration. <https://docs.archer2.ac.uk/user-guide/hardware/>
