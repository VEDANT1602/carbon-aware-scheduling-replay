# How much does a one-hour deferral change the carbon account of a compute queue?

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

21 November 2026

### Abstract

An HPC dispatcher deciding whether to wait must choose before it knows the job’s duration or the future grid intensity. We replayed 76,765 dated ARCHER2 job starts across two weeks in March 2022. A capacity-limited dispatcher compared the previous day’s grid intensities at three possible start times and otherwise used first-in, first-out service. In a scenario where every job of at most four nodes could wait for up to an hour, estimated compute emissions for all released jobs fell by 50.33 kg (0.092%) in week one and 17.83 kg (0.024%) in week two. Mean additional wait across the full job population was 21.8 and 26.9 minutes. Two and five nonparticipants also waited for capacity. Small gross changes in a retrospective carbon account leave open whether the service would save energy or emissions after accounting for controller overhead, unrecorded site constraints and users’ delay preferences.

## A decision with an unknown finish time

A dispatcher can see a job’s requested node count and the grid signal available when the job arrives. Its actual finish time lies in the future. This distinction changes what can be evaluated from an allocation log. We compare starting an available job immediately with selecting among starts 0, 30 and 60 minutes later, using only yesterday’s intensity at those times. The contribution is a complete queue replay with the effect on jobs outside the participating group explicitly charged to the policy.

Production carbon-aware systems use forecasts and capacity controls [1]. The opportunity also depends on workload flexibility and grid variation [2]. COAST offers an informative example [3]. Its authors filtered 165,887 jobs from the CEA-Curie 2011 trace into 224 day-long windows and paired those windows with randomly aligned 2025 British intensity. They assumed 10 W/core and modeled deadlines. Their held-out comparison reported a 15.4% carbon reduction and 1.5 hours of added average waiting against their earliest-feasible observed baseline. Our percentage covers all released jobs in two calendar-matched UK weeks, including large ineligible jobs. The two estimates answer different operating questions.

## What the dispatcher sees

The ARCHER2 allocation release provides UTC starts, ends and allocated nodes [4]. We take the starts in 7–13 and 14–20 March 2022 as the times at which jobs become available. The release has no submission times, reservations, documented deadline or opt-in field. This convention reconstructs recorded starts in an unshifted queue. It cannot recover users’ original queue waits. Jobs already running at the start of each week occupy nodes until they complete. All released jobs count until their actual simulated completion, including jobs that extend beyond Sunday. Each weekly experiment starts with its own observed carry-in.

At release, a job using one to four nodes enters a hypothetical opt-in cohort. We vary the share deterministically by hashing a week-specific input-row index. A participating job compares the previous day’s realized national average intensity for each candidate’s starting half hour [7]. Ties take the earlier time. This rule needs no runtime prediction and charges no network round trip because the table is resident in memory. The 24-hour lag makes every signal available in calendar time before the proposal, subject to the assumption that the historical estimate was published by then. First-publication timestamps and subsequent corrections are unavailable.

Jobs enter the ready queue in order of proposed eligibility, with a stable tie break. When the head fits on the free nodes, it starts. The event engine learns completion after the observed duration elapses. It never exposes future jobs, occupancy or realized duration to the proposal rule. The pool has 5,860 interchangeable nodes, the published system total [8]. Memory classes, maintenance, backfill, network topology, runtime changes after shifting and service priorities are absent. Capacity blocking can extend waits beyond the selected offset.

## The carbon denominator includes the entire release cohort

For each job we integrate observed national half-hourly intensity across every second of its execution, weighted by its node count and an assigned W/node. A separate March 2022 ARCHER2 job-step energy dataset yielded 953,798 positive observations among 966,839 completed steps after filtering. Median measured compute power was 512.18 W/node and the interquartile range was 438.18–541.10 W/node [5,6]. Individual step energy cannot be joined to the anonymized allocation records. A common factor scales absolute mass and cancels from percentages. Idle system power, marginal emissions and cooling are outside this account.

For the full-participation one-hour scenario, the weekly all-job baseline was 54,567 and 74,217 kg, of which participating jobs represented 11,925 and 15,616 kg. At 30 minutes of permitted deferral, full-queue percentage savings were 0.0476% and 0.0123%. With a 60-minute horizon but only a quarter of small jobs participating, savings were 0.0241% and 0.0069%. Each percentage is a comparison with the same unshifted release cohort. On five of the fourteen release days the one-hour full-participation policy increased the cohort’s emissions.


| Weekly outcome, 60-minute horizon | 7–13 Mar | 14–20 Mar |
| --- | --- | --- |
| All jobs released | 38,794 | 37,971 |
| Eligible and participating | 32,246 | 32,717 |
| Jobs delayed | 16,263 | 19,049 |
| Nonparticipants delayed | 2 | 5 |
| Peak occupied nodes | 5,858 | 5,860 |
| Gross carbon reduction (kg) | 50.33 | 17.83 |
| Reduction / all-job baseline (%) | 0.0922 | 0.0240 |
| Reduction among participants (%) | 0.4221 | 0.1144 |
| Mean delay, all jobs (min) | 21.76 | 26.92 |
| Mean delay, participants (min) | 26.18 | 31.25 |
Matched weekly carbon accounts and waiting times. Full hypothetical participation by small jobs. Delay includes waiting for capacity.

## Which costs would erase the benefit?

The number of candidate evaluations was 96,738 and 98,151 in the two full-participation weeks. If each evaluation consumed E joules at the release-time grid intensity, the emission charge would be E times the sum of those intensities divided by 3.6 million. Dividing the weekly gross benefit by that coefficient gives 14.65 and 4.13 kJ per evaluation. These are break-even budgets under a specified accounting rule. Site-wide system energy, agent polling and remote forecast retrieval would require their own measured cost boundaries.

The actual three-candidate decision function was timed on the first week’s 32,246 participating releases. Thirteen alternating-order pairs compared the resident-table lookup and choice with an immediate-start loop on the same timestamps. Median incremental elapsed time was 0.81 microseconds per proposal on one x86-64 Python 3.12 host. This measures local policy computation only. There was no readable package-energy counter or scheduler power meter on that host, so energy per lookup and net carbon benefit remain unmeasured. The supplied script also reads a Linux package-energy counter when accessible.

## What a live trial must establish

The sign changes across individual release days show the limitation of using yesterday’s grid conditions to select a later slot. In both weeks the full-cohort benefit was below one tenth of one percent, while some jobs outside the opt-in group incurred a wait. The operator deciding whether to implement this policy needs a release-time signal with known publication history, explicit user permission to defer and measured incremental controller energy on the deployment machine. The trace supports estimating the gross trade-off conditional on those scheduling assumptions.

## Data and code availability

The supplement includes the two dated allocation and intensity subsets, the extra grid intervals needed for the last completions, source attribution, model code, daily results and the paired timing log. Sources [4], [5] and [7] provide upstream data. The related data extraction is pinned at https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/a31ba8a660c26067dddd8121c313332d9939a89b .

[Study files, software and source records](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/main/study)

## Author and disclosures

Vedant Thaker is the sole author and set the research question. OpenAI Codex assisted with implementing the forward trace replay, checking the accounting, timing the lookup implementation and drafting the analysis.

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
