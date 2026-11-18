# When does waiting repay the cost of a carbon forecast?

**Vedant Thaker**  
Working paper · 18 November 2026

## Abstract

The carbon cost of looking for a cleaner time slot can outweigh the emissions saved by moving work into it. We test that trade-off using public AWS load-balancer request counts. Seven days establish service capacity. The following seven supply 117,154 count units, each treated as a hypothetical deferrable job. Two scheduling policies share the same capacity and deadlines. Their comparison accounts for work energy, idle energy, scheduling overhead and grid intensity. With one hour of slack and an aligned two-frequency grid signal, ranking 13 candidate slots saves an estimated 33.91 g CO2e in work emissions. Charging two joules per lookup leaves a net saving of 28.10 g, or 2.33% of the baseline total. The median daily 95th-percentile start delay rises from zero to 60 minutes. A two-hour forecast lag instead adds 36.75 g at the same deadline. For the aligned case, the break-even cost is 11.67 joules per candidate lookup. The public trace measures request counts. Power, grid conditions and job deadlines are modeled.

## 1. The cost of making the decision

A forecast is useful only if a job can wait, a cleaner slot still has room, and the extra decision work costs less than the shift saves. Radovanovic et al. describe production workload shifting using forecasts and capacity controls [1]. Theodoropoulos et al. evaluate shared forecasting for proactive autoscaling and explicitly study service performance and resource consumption [2]. Here the decision is narrower. With a fixed pool, what price can a scheduler pay to inspect future slots before the carbon arithmetic changes sign?

The benchmark couples an observed arrival profile to a small reservation simulator. Its contribution is an auditable break-even calculation that can be recomputed for different power assumptions. The same arrivals drive all comparisons. A flat grid provides a check on the emission calculation. A shifted forecast lets the analysis change the information available to the scheduler while keeping the true grid, the jobs and the capacity fixed.

## 2. What the trace actually measures

The input is one request-count series from the real AWS CloudWatch collection in the Numenta Anomaly Benchmark [3,4]. The public file contains 4,032 timestamped counts from April 10 through the first 40 minutes of April 24, 2014. Restricting the replay to April 10–23 gives fourteen 24-hour periods on a five-minute grid whose first timestamp is 00:04. The eight records on the partial final day are excluded. Eight expected timestamps inside the fourteen days are absent. Capacity is the ceiling of the 95th percentile of observed counts on April 10–16, giving 182 unit jobs per bin. April 17–23 supplies seven evaluation days. Three bins in those seven days are missing. The main analysis inserts zero arrivals in those bins. A sensitivity run inserts the training median of 53.

One observed count unit becomes one unit of schedulable work. Each day starts a fresh replay. This assumes equal service demand and an asynchronous application with permission to delay the work. The original series is a load-balancer metric. A user-facing HTTP request and an offline task have very different latency requirements. The replay borrows the recorded demand variation and evaluates a hypothetical batch service. Each bin admits the entire count at its boundary. Delay is measured to the assigned service bin, so sub-bin response time cannot be estimated.

## 3. Reservations, grid assumptions and accounting

The baseline inspects available capacity in chronological order. The carbon policy considers slots between arrival and the latest permitted service bin, inclusive, and ranks them by forecast intensity. Equal scores favor the earlier slot. Each batch fills the ranked slots until it is fully placed. Capacity assigned to an earlier batch remains reserved. Any work left after the deadline takes the first available later slot, and its count enters the late-job metric. A full bin holds 182 jobs under either policy. Runs check that all arrivals are served exactly once and capacity is respected in every bin.

Three artificial grids are evaluated. The flat grid stays at 400 g CO2e/kWh. The daily grid adds a cosine of amplitude 150 with a 24-hour period and a peak three hours after the start. The mixed grid adds a second cosine of amplitude 65 with a four-hour period and a peak 30 minutes after the start. The scheduler receives either the true curve or the same curve lagged by two, six or twelve hours. All emission calculations use the original true curve. Phase is an experimental treatment, with no assumed probability of occurring in a particular electricity system.

Energy per job is 36 J in the main comparison. A common idle allocation of 10 W runs for 26 hours per independent day, including two hours to drain the queue. This explicit accounting window includes empty bins under both schedules. Sorting and obtaining a forecast have no measured power trace. The model charges the forecast policy an incremental 2 J per candidate slot examined at batch arrival. A one-hour allowance means 13 lookups per nonempty batch, regardless of how quickly it finds capacity. Common reservation work is outside the incremental charge. A platform that caches curves across batches or runs a costly inference once per day needs a different cost model.

For a given schedule, multiply each bin's job energy, idle energy and lookup energy by its grid intensity, then divide by 3,600,000 to convert joules to kWh. Gross saving is the baseline workload emissions minus the forecast schedule's workload emissions. Dividing this quantity by the grams attributable to one joule per lookup yields the break-even joules per lookup. A negative gross saving means that free lookups would already lose carbon. Both throughput and deadline are fixed when comparing the policies within a row.

## 4. An aligned forecast buys time at a price

Table 1 gives the seven-day paired totals on the mixed grid. Positive saving means lower modeled emissions for the forecast policy. The deadline measures allowable start delay. The p95 column reports the median of the seven daily 95th-percentile delays for the forecast policy. The corresponding baseline median is zero in every row. Both planners serve all 117,154 jobs.

| Allowance | Forecast lag | Forecast p95 | Forecast late | Gross saving, g | Net saving, g |
| --- | --- | --- | --- | --- | --- |
| 30 min | 0 h | 30 min | 0 | 18.23 | 15.09 |
| 30 min | 2 h | 30 min | 1,085 | -16.64 | -19.77 |
| 60 min | 0 h | 60 min | 0 | 33.91 | 28.10 |
| 60 min | 2 h | 60 min | 0 | -30.93 | -36.75 |
| 60 min | 6 h | 60 min | 0 | -33.00 | -38.81 |
| 60 min | 12 h | 60 min | 0 | 27.05 | 21.23 |

With aligned forecasts and 60 minutes of slack, workload emissions fall from 458.00 to 424.08 g. Both policies incur 750.22 g of allocated idle emissions. The forecast policy inspects 26,169 candidate slots, adding 5.81 g. The totals are 1,208.22 and 1,180.12 g. Every evaluation day has positive net savings in this configuration, ranging from 2.63 to 5.09 g. Mean delay rises from 0.34 to 32.42 minutes. An application with a 60-minute deadline could accept that change while a service owner tracking user wait would see a substantial degradation.

The two-hour forecast shift reverses the fast four-hour component. It can place a reservation near a true intensity peak. At 30 minutes of slack, it also reserves slots later needed by new arrivals, producing 1,085 late jobs versus zero under the baseline. The 12-hour lag preserves the fast component's phase and reverses the daily component. Net savings reappear. The nonmonotonic pattern follows from the chosen frequencies and the observed arrival times. It cautions against using one scalar forecast delay to predict results on a different grid.

## 5. Which assumptions move the break-even point?

On the aligned mixed grid, the gross saving can cover 11.67 J per lookup at 36 J per job. Halving job energy to 18 J lowers the threshold to 5.83 J and the net saving at 2 J per lookup to 11.14 g. Doubling job energy to 72 J raises the threshold to 23.33 J. Common idle power changes the percentage while leaving the grams saved unchanged. At idle powers of 0, 10 and 50 W, the 28.10 g saving represents 6.14%, 2.33% and 0.67% of baseline emissions, respectively. This is why a reported percentage needs its power boundary.

On a flat grid, both schedules produce the same service pattern and identical workload emissions. The lookups then add 5.82 g in the 60-minute trial. On the daily-only grid the aligned forecast saves 5.29 g net, far below the mixed-grid result. Replacing three absent test counts with the training median increases replay demand to 117,313 and changes the aligned mixed-grid saving to 28.12 g. These are sensitivity analyses over one trace. The seven days provide no estimate of variability across data centers, seasons or grid regions.

## 6. Implications for a measured trial

The arithmetic suggests three measurements for a deployment study. First, identify which jobs can actually wait and record their deadlines. Next, meter both task execution and incremental forecast service on the intended hardware, including the effect of sharing forecasts across jobs. Finally, replay forecasts as they were issued against grid observations from the same time and region. Grid-average operational accounting and avoided marginal emissions answer different questions. This study models an assigned intensity curve and therefore cannot estimate avoided power-system emissions.

## Reproducibility

Run `python run.py` with Python 3.11 and NumPy 1.26. The archive contains the input CSV with the upstream Numenta license, and `results.csv` stores 1,008 matched daily condition records. Each row reports request count, late count, delay, workload grams, common idle grams and the coefficient needed to reprice lookup energy. The source is the public AWS series at [4]. No cloud instances, energy meters or paid APIs were used.

## Research and writing assistance

Vedant Thaker supplied the research brief and source materials. OpenAI Codex assisted with study design, implementation, execution, literature review and drafting. Clever Humanizer suggested edits to the abstract. The final wording was checked against the analysis.

## References

[1] A. Radovanovic et al. Carbon-Aware Computing for Datacenters. IEEE Transactions on Power Systems. Author preprint, 2021. https://arxiv.org/abs/2106.11750

[2] T. Theodoropoulos, Y. S. Patel, P. Townend, I. Korontanis, A. Makris and K. Tserpes. GraphOpticon: A Global proactive horizontal autoscaler for improved service performance & resource consumption. Future Generation Computer Systems, 2026. https://zenodo.org/records/17804256

[3] A. Lavin and S. Ahmad. Evaluating Real-time Anomaly Detection Algorithms: The Numenta Anomaly Benchmark. 2015. https://arxiv.org/abs/1510.03336

[4] Numenta. Real AWS CloudWatch load-balancer request series, elb_request_count_8c0756.csv. Numenta Anomaly Benchmark data repository. https://github.com/numenta/NAB/blob/master/data/realAWSCloudwatch/elb_request_count_8c0756.csv
