# How much energy can a carbon-aware scheduler spend evaluating a later start?

**Vedant Thaker**  
Independent Researcher, Jeffersonville, Indiana, United States  
Correspondence: vthaker1@asu.edu  
21 November 2026

## Abstract

We estimate the energy per candidate start that would erase the modeled emissions benefit of delaying compute work. Two consecutive weeks of ARCHER2 allocations were paired with the Great Britain grid series for the same dates. March 2022 job-step meters supplied a median of 512 W per allocated node. A scheduler using the previous day’s intensity could move short allocations by up to one hour under an imposed flexibility allowance. It moved 8,870 of 18,650 eligible allocations in week one and 14,521 of 24,896 in week two. Modeled gross reductions were 11.58 and 12.66 kg CO₂. The break-even costs were 5,680 and 3,905 J per candidate start. Gross emissions increased on one day in each week. In a separate 2014 request-count replay, a candidate represented one slot for a whole batch of smaller, hypothetical jobs. Its break-even was 11.67 J per lookup under a prescribed grid curve. Neither trace reports permission to postpone jobs or meters the scheduler’s incremental energy. The estimates price specified decisions and identify the measurements needed to evaluate a live deployment.

## 1. Pricing the work of choosing a start time

Carbon-aware scheduling can change when electricity is consumed while leaving total job energy fixed. Radovanović et al. deployed forecast-based capacity controls for flexible data-center workloads [1]. Sukprasert et al. quantified limits on workload shifting across 123 grid regions [2]. Feng et al. evaluated congestion-aware starts for HPC jobs using a CEA-Curie workload, UK grid data from another period, and modeled delay tolerance [3]. These studies motivate a narrower accounting question. Given a particular policy and number of candidate starts, what incremental scheduling energy would consume its modeled benefit?

We first pair UK node allocations with the national grid record on their actual dates and retain observed background occupancy. A separate same-system meter dataset calibrates power. Two adjacent weeks give an observed repeat at the same site. An earlier, controlled request-count calculation uses a smaller unit of work and a deliberately misaligned forecast to expose when the sign can change. No intervention was performed on either service.

## 2. A signed break-even budget

For each schedule, integrate the grid intensity across the duration of each allocation and multiply by its assigned power and node count. If intensity is in g CO₂/kWh, time in seconds and power in watts, divide the product by 3,600,000 to obtain grams. Let G be baseline minus shifted job emissions. Let K be the sum, over decision times, of the number of incremental candidate evaluations times the intensity at the decision, divided by 3,600,000. If each costs e joules, net saving in grams equals G − eK. For K > 0 and G > 0, break-even is G/K joules per candidate. A negative G means even a cost-free scheduler increases modeled emissions. For G = 0, a positive cost produces a loss.

The incremental budget includes evaluating all advertised offsets, including rejected offsets. It excludes admission and reservation work common to both schedules. The threshold assumes evaluation at the original start on the same grid. A shared daily forecast, cached service, or separate control-plane region needs a different count and intensity. A candidate in the UK study is one potential start for a multi-second or multi-hour allocation. In the count experiment it is one five-minute service bin evaluated once for an entire arrival batch. Their numerical budgets therefore price different operations.

## 3. Allocations, grid estimates and node meters

The ARCHER2 Slurm release contains allocated node counts and observed starts and finishes [4]. We used March 7–13, 2022, the first complete Monday–Sunday block of that month, and repeated the analysis on March 14–20, all in UTC. Include every positive-duration, positive-node allocation overlapping the focal week or its two-hour drain. This retains 39,746 and 38,805 background and eligible records, respectively. A candidate for movement must start and finish within the week, use at most four nodes and last at most two hours. These thresholds define a tractable class of short allocations and assert no service entitlement. The file omits submit times, user deadlines, consent, node identities and dependencies.

The HPC-JEEP archive recorded 966,839 completed ARCHER2 job steps in March 2022 [5]. For the 953,798 steps with positive energy, nodes and elapsed duration, we divided recorded joules by node-seconds. The lower quartile, median and upper quartile across individual steps were 438.18, 512.18 and 541.10 W/node. We use the median as a constant across candidate starts and examine both quartiles. The project report documents node energy counters and missing readings, and excludes facility overhead from these node measurements [6]. An accounting step and an anonymous Slurm allocation have different identifiers. We apply a distribution of measured powers without assigning a particular meter reading to any allocation.

NESO supplies half-hourly GB national average intensity and an archived forecast [7]. Its actual field is a generation-based estimate in g CO₂/kWh. For the main decision rule, an interval takes the value from the corresponding half-hour of the previous day. Even the longest candidate ends before that historical profile approaches decision time. Historical data may incorporate later corrections. The two diagnostics rank with the archived forecast and with the realized grid profile. The archive has no forecast issue timestamps. Neither diagnostic evaluates a guaranteed day-ahead feed. We use the realized series to score all schedules.

## 4. Moving an occupied interval without exceeding the observed peak

The comparison starts with all allocations in place. Traverse eligible intervals in original start, end and node-count order. Momentarily free each interval, evaluate starts from the original time through 0, 30, 60 or 120 minutes of additional delay in half-hour increments, and keep duration and node count fixed. Reject any placement that would push total occupied nodes over the week’s original peak. Of the remaining starts choose the one with lowest predicted integrated intensity, taking the earliest on ties. The original slot is always an available placement at that step. With future background allocations fixed, this is a retrospective replay with knowledge of durations and aggregate occupancy. It assumes interchangeable nodes. Site reservations, network topology and workflow precedence could further restrict feasibility.

Under the 60-minute previous-day rule, week-one eligible job attribution changed from 448.31 to 436.73 kg CO₂, with 55,950 candidates examined. Average delay across all eligible jobs was 24.72 minutes. In week two the corresponding values were 578.60 to 565.94 kg, 74,688 candidates and 31.67 minutes. The count rose by a third while gross savings rose only 9.3%, and the grid intensity at decision times also changed. These changes lower the second week’s budget per candidate. At 2 J each, modeled net savings were 11.575 and 12.652 kg. The 2 J value illustrates the equation and has no basis in a physical controller measurement.

Gross daily changes at 60 minutes ranged from −0.205 to 3.287 kg in week one and −1.176 to 4.742 kg in week two. Each week had six positive days. At the two empirical power quartiles the primary week’s 60-minute budget varied from 4,859 to 6,001 J/candidate. At the median power, ranking with the archived forecast gave 5,891 and 4,810 J/candidate in the respective weeks. The greedy rule with realized intensity scores gave 8,178 and 6,667 J/candidate. Perfect scores on a greedy search give a hindsight comparison without proving a global optimum. Table 1 summarizes the main prospective-signal approximation. The two consecutive weeks do not furnish independent season or site replicates.

| Week, March | Slack (min) | Moved | Gross kg CO₂ | J/candidate |
| --- | --- | --- | --- | --- |
| 7–13 | 0 | 0 | 0.00 | 0 |
| 7–13 | 30 | 7,989 | 6.41 | 4,715 |
| 7–13 | 60 | 8,870 | 11.58 | 5,680 |
| 7–13 | 120 | 9,668 | 19.43 | 5,718 |
| 14–20 | 0 | 0 | 0.00 | 0 |
| 14–20 | 30 | 13,375 | 6.42 | 2,971 |
| 14–20 | 60 | 14,521 | 12.66 | 3,905 |
| 14–20 | 120 | 16,150 | 25.14 | 4,654 |

Table 1. Previous-day intensity signals and a median 512.18 W/node. Eligible totals are 18,650 and 24,896. Aggregate concurrency stayed at or below the original peaks of 5,760 and 5,774 nodes. A zero-slack evaluation has no gross benefit.

## 5. What a reservation clock establishes

An observed start is a lower bound chosen for this counterfactual. It reveals neither an acceptable latest start nor a user’s willingness to wait. We checked the separate French Grid’5000 OAR archive to see what its explicit reservation records add [8]. Of 69,189 linked reservation records, 48,212 had positive runtime and valid windows. In every such record, submission plus waiting equalled the stored reservation start, and reservation duration equalled observed runtime. Requiring the entire run to remain inside that recorded window leaves zero room to move it. This identity describes the stored field semantics and does not establish that the user would have declined a different reservation. No French record entered the UK carbon calculation.

Whole-job SLA compliance therefore remains unidentified. With no discretionary movement the gross scheduling benefit vanishes, as the zero-slack rows show. The positive-slack rows quantify the value of a permission that an operator would need to record independently. We acknowledge the Grid’5000 and OAR teams, including Franck Cappello, Olivier Richard and Nicolas Capit, and the Grid Workloads Archive for the reservation observations.

## 6. A controlled sign reversal in the request-count replay

The legacy comparison uses Numenta’s AWS load-balancer count file with 4,032 observations [9,10]. April 10–16, 2014 sets a five-minute capacity of 182 using the ceiling of the observed 95th percentile. April 17–23 supplies 117,154 count units under zero imputation in three missing bins. A unit becomes one hypothetical 36 J job. A policy can inspect 13 bins per nonempty batch with a 60-minute allowance. It reserves capacity in forecast order and serves any overdue jobs in the next available later bin. A common idle draw of 10 W is charged for each day’s 26-hour accounting window. The flat, daily and two-frequency intensity curves are imposed. The mixed case adds 24-hour and four-hour cosines with amplitudes 150 and 65 g CO₂e/kWh to a 400 g baseline.

With the forecast aligned to the mixed grid, earliest and ranked scheduling served all jobs on time. The gross saving of 33.91 g CO₂e fell to 28.10 g after 26,169 candidate lookups priced at 2 J each. The implied threshold is 11.67 J/lookup, and mean delay rose from 0.34 to 32.42 min. A two-hour lag reverses the four-hour component and produces a 36.75 g net penalty. With a single weekly queue and drain the penalty is 36.85 g. Halving and doubling the assumed work energy shift the aligned threshold to 5.83 and 23.33 J/lookup. Under the flat grid, extra lookups add 5.82 g. Replacing the three missing bins with the training median of 53 changes aligned net savings to 28.12 g. These are g CO₂e from imposed curves. The UK results use the provider’s g CO₂ unit.

## 7. What a deployment would have to measure

Within these two March weeks, imposing one hour of flexibility on selected allocations produced positive gross savings in aggregate and occasional daily losses. Whole-node power, a GB average carbon signal, known background occupancy and fixed durations condition that result. Holding job energy constant allocates it to different times. Changes in machine idle power, cooling, local grid mix and marginal power-system emissions could give different physical outcomes.

A deployment test needs signed-off job windows, as-issued forecast histories, node-level placement rules and workload-specific meters. It also needs incremental energy for the deployed decision service, including any remote forecast generation or caching allocated to it. The analysis host exposed no accessible powercap energy counter, MSR device or wattmeter for that measurement. External ARCHER2 meters established a compute-power scale only. Until scheduling energy and authorized flexibility are measured jointly, G/K is a budget against which a deployment can be tested.

## Data and code availability

The accompanying supplement includes the dated UK allocation subsets, GB intensity, meter percentiles, reservation audit, both weeks’ outputs and source hashes. DATA-SOURCES.md identifies the inputs, attribution and transformations. Run python dated_replay.py and python check_dated.py, then repeat both commands with --repeat. All four runs use standard Python. The original count replay, upstream data notice and 1,008 daily rows are available in the baseline repository. Environment locks, run.py, verify.py, a row comparator and the continuous-week replay accompany that experiment.

[Pinned baseline](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/dea2cea99bfc52fb21a7321fdc0d676060e5472d) · [Revision code and data](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/main/revision/supplement) · [Preparation record](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/blob/main/revision/PREPARATION.md)

## Computational verification

A separate event sweep checked the candidate decisions saved for both 60-minute previous-day replays, the multiset of eligible allocations, allowed delays, node peaks, integrated job attribution and break-even values. Raw source digests and transformations are listed in DATA-SOURCES.md. The legacy verifier checked the count digest and energy arithmetic. A fresh calculation matched all legacy scenario keys and integer fields, with maximum absolute floating-field difference below 6 × 10⁻¹⁴.

## Author contribution

Vedant Thaker is the sole author. He designed the original carbon-aware scheduling study, wrote its manuscript, developed its original software, and requested the comparisons and checks reported in this revision.

## Use of computational assistance

OpenAI Codex assisted with the scheduling replays, preparation of the trace-based comparisons, accounting and time-boundary checks, and source verification, as well as literature checks and preparation of the revised text. The author set the research question and requested the revision.

## Funding

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

## Competing interests

The author declares no competing interests.

## References

[1] A. Radovanović et al. Carbon-Aware Computing for Datacenters. IEEE Transactions on Power Systems 38, 1270–1280 (2023). https://doi.org/10.1109/TPWRS.2022.3173250

[2] T. Sukprasert, A. Souza, N. Bashir, D. Irwin and P. Shenoy. On the Limitations of Carbon-Aware Temporal and Spatial Workload Shifting in the Cloud. EuroSys, 924–941 (2024). https://doi.org/10.1145/3627703.3650079

[3] W. Feng, A. Dasgupta, Z. D. Tekler, S. Ahuja, J. Zheng and X. Jiang. COAST: Congestion-Aware Start-Time Recommendations for Carbon-Aware HPC Jobs. arXiv:2609.05443v1 (2026), preprint. https://arxiv.org/abs/2609.05443v1

[4] A. Jackson and I. Lamprakis. HPC System Usage Data, v1.0. ARCHER2 Slurm summary dataset (2024). https://doi.org/10.5281/zenodo.14284189

[5] A. Turner and A. Basden. HPC-JEEP: Energy Usage on ARCHER2 and the DiRAC COSMA HPC services dataset (2022). https://doi.org/10.5281/zenodo.7128646

[6] A. Turner and A. Basden. HPC-JEEP: Energy Usage on ARCHER2 and the DiRAC COSMA HPC services. Technical report (2022). https://doi.org/10.5281/zenodo.7137390

[7] National Energy System Operator and project partners. Carbon Intensity API, national half-hourly GB intensity and forecast series. See DATA-SOURCES.md for the two dated API requests. https://carbonintensity.org.uk/

[8] A. Iosup and M. Jan, trace contributors. Grid Workloads Archive, GWA-T-2 Grid5000. Archived OAR jobs and reservations. https://atlarge-research.com/gwa-t-2/

[9] Numenta. NAB, realAWSCloudwatch, elb_request_count_8c0756.csv. Input series, Git blob c2c83f9f470653d5db71f8aa6a038a98e075c7ae. https://github.com/numenta/NAB/blob/master/data/realAWSCloudwatch/elb_request_count_8c0756.csv

[10] A. Lavin and S. Ahmad. Evaluating Real-Time Anomaly Detection Algorithms – The Numenta Anomaly Benchmark. IEEE International Conference on Machine Learning and Applications, 38–44 (2015). https://doi.org/10.1109/ICMLA.2015.141
