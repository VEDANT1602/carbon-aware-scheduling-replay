# The carbon opportunity in one hour of flexibility at ARCHER2

Vedant Thaker  
Independent Researcher, Jeffersonville, Indiana, USA  
vedant.thaker1602@gmail.com

Scheduling study

**Research period (author-reported)** · September 19–October 1, 2026 &nbsp; | &nbsp; **Manuscript revised** · November 21, 2026

### Abstract

How much could a scheduler save by choosing among three starts within one hour? A replay of 76,765 observed ARCHER2 allocations in two March 2022 weeks compares yesterday’s grid signal with a scheduler given the future grid intensity and each job’s duration. Using the recorded start as the simulated release, the previous-day policy reduced estimated gross compute emissions across all jobs by 50.33 kg (0.0922%) and 17.83 kg (0.0240%). Mean additional waits were 21.76 and 26.92 minutes. An offline schedule that preserved every nonparticipant’s start attained 220.34 and 167.62 kg. Independent best starts give ceilings of 221.58 kg (0.4061%) and 167.62 kg (0.2258%) under the same protection. A better signal could therefore improve both weeks substantially relative to the tested policy, while the absolute opportunity remained below half a percent of the full carbon account. Submission times and delay permissions are absent from the allocation data.

## The decision and the trace

Production carbon-aware systems use forecasts and capacity controls [1]. The attainable saving depends on workload flexibility and grid variation [2]. A small observed benefit could reflect poor forecasts or jobs with little scope for shifting. We separate these explanations by measuring savings under yesterday’s signal and bounding the best possible savings on the same two weeks.

COAST [3] filtered the CEA-Curie 2011 trace to 165,887 jobs in 224 daily windows, randomly aligned with 2025 British intensity. Its assumed power was 10 W/core and its deadlines were assigned. The authors reported 15.4% lower estimated carbon with 1.5 hours of additional mean waiting. Our denominator includes all weekly releases, with an hour of proposed flexibility limited to jobs of at most four nodes.

The ARCHER2 release provides UTC starts, ends and allocated nodes [4]. Each job that began during 7–13 or 14–20 March 2022 enters the experiment at that recorded start. Jobs already running on Monday retain their outstanding work. The simulated immediate-start schedule fits within the 5,860 installed nodes [8] and reproduces every recorded start by construction. All subsequent waiting is added by the simulation. A policy effect on the actual site's submission queue would require submission times, service priorities, reservations and authorized slack. The weeks are separate experiments; a job counts through its completion even if it finishes after Sunday.

## Two ways to assign starts

In the forward replay, release time and node count determine eligibility. Every one-to-four-node job in the main scenario can propose starting immediately, 30 minutes later or 60 minutes later. It chooses the lowest national grid intensity observed in the corresponding half hour the previous day [7], breaking ties toward the earlier start. A first-in, first-out queue launches ready jobs as capacity permits, including larger jobs that cannot request a delay. Proposals have a one-hour limit. Capacity blocking can extend realized waits. The policy has no access to future jobs or durations. Historical first-publication timestamps for intensity are unavailable.

The offline comparison knows every duration and realized intensity. For each job it integrates intensity across the entire run at each of the same three starts. First, the best proposals enter the identical queue. Second, to impose a hard one-hour limit and preserve each nonparticipant’s original start, we compare schedules with those protections. A feasible procedure begins at the unshifted timetable and tries the shifts in descending order of individual saving, accepting only moves that keep every interval within capacity. If all individually preferred starts are jointly feasible, it takes them directly. It never shifts carry-in jobs. The same capacity check can repair previous-day preferences for a matched signal comparison.

For a participant i, let Eᵢ(k) be its estimated emissions starting k minutes after release. The largest possible individual saving is Eᵢ(0) − min{Eᵢ(0), Eᵢ(30), Eᵢ(60)}. Summing these savings drops the capacity constraint. It gives an upper bound for every schedule that fixes nonparticipants and honors the three starts. A capacity-feasible schedule gives a lower bound on the best attainable saving. These bounds do not cover continuous choice of starting times or permission to move larger jobs.

## What enters the carbon account?

The calculation integrates half-hourly national intensity over execution time at second resolution, multiplied by allocated nodes and a common W/node. A separate ARCHER2 energy dataset yielded 953,798 positive job-step readings among 966,839 completed March steps. Measured power per node had median 512.18 W and interquartile range 438.18–541.10 W [5,6]. Individual energy records cannot be joined to these anonymized jobs. This power factor scales mass and cancels from percentage changes. The account excludes site idle power, cooling and marginal grid effects.

| Previous-day queue, 60-minute proposal limit | 7–13 March | 14–20 March |
| --- | --- | --- |
| All jobs / participating jobs | 38,794 / 32,246 | 37,971 / 32,717 |
| Baseline CO₂, all jobs (kg) | 54,567.443 | 74,216.693 |
| Baseline CO₂, participants (kg) | 11,924.807 | 15,615.901 |
| Saved CO₂, participants (kg) | 50.3360 | 17.8624 |
| Saved CO₂, nonparticipants (kg) | −0.0053 | −0.0287 |
| Saved CO₂, all jobs (kg) | 50.3307 | 17.8337 |
| Saving / all-job baseline (%) | 0.0922 | 0.0240 |
| Participant saving / participant baseline (%) | 0.4221 | 0.1144 |
| Jobs delayed / nonparticipants delayed | 16,263 / 2 | 19,049 / 5 |
| Mean delay, all jobs (minutes) | 21.76 | 26.92 |
Table 1. All jobs released within each week count through completion. A negative saving is an increase. All displayed numbers are rounded after aggregation.

In week two, five delayed nonparticipants incurred an additional 0.0287 kg. The 17.8624 kg saving for participants divided by their 15,615.901 kg baseline gives 0.1144%. Subtracting the additional emissions yields the 17.8337 kg all-job saving. Over the fourteen release days, the one-hour policy increased emissions on five. Reducing the proposal horizon to 30 minutes gave full-queue savings of 0.0476% and 0.0123%. Allowing one hour for a deterministically selected quarter of small jobs gave 0.0241% and 0.0069%.

## How much could perfect information buy?

| Gross saving, all jobs (kg) | 7–13 March | 14–20 March |
| --- | --- | --- |
| Previous-day signal, actual simulated queue | 50.33 | 17.83 |
| Perfect information, same simulated queue | 221.11 | 167.62 |
| Protected starts, previous-day preferences | 50.33 | 17.33 |
| Protected starts, feasible perfect-information schedule | 220.34 | 167.62 |
| Protected starts, capacity-relaxed ceiling | 221.58 | 167.62 |
Table 2. The first two rows allow incidental queue delays. The last three keep every nonparticipant at its recorded start and every participant at one of the three candidate starts.

Under the identical queue rule, perfect information improved the gross account in both weeks. In week one, 24 nonparticipants waited and 60 jobs exceeded one hour, with a maximum of 61 minutes 55 seconds. That row therefore prices a one-hour proposal horizon. A hard one-hour guarantee calls for the protected schedule. Its week-one upper bound would need 5,957 nodes at its busiest instant; the feasible schedule stays within 1.25 kg of that bound on the available 5,860 nodes. In week two the individual choices fit within 5,843 nodes and attain the exact optimum. These bounds apply to the supplied trace and power model.

With protected starts on both sides, the previous-day rule captures 22.7% and 10.3% of the respective ceilings. Even an ideal policy could save at most 0.4061% and 0.2258% of the all-job baselines under these permissions. Forecast quality leaves room for improvement. The small upper bounds show how little this particular allocation mix, time window and grid trace could deliver in absolute terms.

## Why lookup timing does little to settle deployment

Charging each candidate read at its release-time intensity gives gross break-even budgets of 14.65 and 4.13 kJ per read (96,738 and 98,151 reads). These budgets are too loose to discriminate between ordinary in-memory implementations. Thirteen alternating paired timing runs on one host put the median incremental elapsed time of a three-candidate proposal at 0.81 microseconds. The run produced no energy measurements. Translating wall time into joules would require measured incremental power. Testing the full service would also require metering polling, forecast retrieval and control overhead. User delay and the small site-level ceiling are the more informative trade-offs in these two weeks.

## Data and code availability

The supplement contains the dated input subsets, meter-based calibration, replay decisions, carbon accounts, oracle calculation and independent checks. Raw sources and redistribution terms are listed against [4], [5] and [7].

[Study files, software and source records](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/main/study)

## Author and disclosures

Vedant Thaker is the sole author. He specified the scheduler comparison, including the need to distinguish forecasting error from limited flexibility. OpenAI Codex assisted with the replay and oracle implementations, numerical checks, source checks and drafting.

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
