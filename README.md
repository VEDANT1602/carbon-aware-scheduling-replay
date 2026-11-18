# When does waiting repay the cost of a carbon forecast?

A scheduler can wait for a cleaner slot, use up the available slack, and still spend more carbon on the decision than it saves. This replay uses observed request counts and an explicit energy budget to calculate how expensive a forecast lookup can be before the saving disappears.

[Read the manuscript (PDF)](manuscript.pdf) · [Read the Markdown version](manuscript.md) · [Inspect the daily results](results.csv)

## Workload and comparison

The input is one AWS load-balancer request-count series from the Numenta Anomaly Benchmark. Seven days in April 2014 set five-minute service capacity at 182 count units. The next seven days supply 117,154 observed count units. For the experiment, each unit becomes a hypothetical deferrable job. Three missing bins in the evaluation period receive zero arrivals in the main replay and the training median of 53 in a sensitivity check. The observed counts carry no job deadlines, service durations, power readings or regional grid intensities.

Both policies reserve slots on the same pool. One picks the earliest available slot. The other ranks available slots by forecast grid intensity, permitting delay up to the same deadline. Any work pushed past its deadline is still served and counted as late. Each schedule accounts for energy per job, idle power over a common meter window, and incremental energy charged to the forecast lookups. The study varies the allowable delay, the forecast's phase error and the shape of the modeled grid curve.

## Findings

For one hour of allowable delay on the mixed grid, the aligned forecast trades waiting time for lower estimated emissions. The main assumptions are 36 J per job, 10 W of idle power and 2 J per candidate lookup.

| Seven-day result | Earliest slot | Aligned forecast |
| --- | ---: | ---: |
| Work emissions | 458.00 g CO2e | 424.08 g CO2e |
| Candidate forecast lookups | 0 | 26,169 |
| Incremental lookup emissions | 0.00 g CO2e | 5.81 g CO2e |
| Total modeled emissions, including idle allocation | 1,208.22 g CO2e | 1,180.12 g CO2e |
| Median daily 95th-percentile start delay | 0 min | 60 min |
| Jobs served late | 0 | 0 |

The gross saving is 33.91 g CO2e and the net saving is 28.10 g, or 2.33% of the baseline total. Dividing the gross saving by the emissions attributable to one joule per lookup gives a break-even point of 11.67 J per candidate. Introducing a two-hour forecast lag makes the forecast policy emit 36.75 g more than the baseline at the same one-hour deadline. The sensitivity follows from the modeled daily and four-hour cycles. Metering a deployment and matching issued forecasts to observed regional grid intensity would test whether these trade-offs hold in practice.

## Reproduce

From the repository root, use Python 3.11, then install the numerical dependency and run the experiment.

```console
python verify.py
python -m pip install -r requirements.txt
python run.py
python verify.py
```

`verify.py` uses the Python standard library and checks the distributed daily results, source counts, energy accounting, delay and break-even calculation. `run.py` reads the included input and rewrites `results.csv`. Its 1,008 rows cover seven evaluation days, two missing-bin treatments, three grid shapes, four forecast lags, three deadlines and two policies. Each row is one day under one configuration.

## Data provenance

The public series is included as [elb_request_count_8c0756.csv](elb_request_count_8c0756.csv). Its original Git blob identifier is `c2c83f9f470653d5db71f8aa6a038a98e075c7ae`. The upstream copyright and permission notice is included in [NAB-LICENSE](NAB-LICENSE). [Upstream data file](https://github.com/numenta/NAB/blob/master/data/realAWSCloudwatch/elb_request_count_8c0756.csv) · [Numenta Anomaly Benchmark paper](https://arxiv.org/abs/1510.03336)

Maintained by Vedant Thaker.
