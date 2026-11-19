# The carbon cost of looking for a cleaner time slot

The seven-day replay starts with 117,154 observed load-balancer count units. It treats each as a deferrable job and gives the scheduler a forecast of grid intensity. The request counts come from AWS CloudWatch via the Numenta Anomaly Benchmark. Job energy, deadlines, idle power and the grid curve are assumptions of the replay. [Workload](elb_request_count_8c0756.csv) · [Grid model](run.py#L35)

On April 17, the aligned forecast did 3,731 candidate lookups for 19,646 arrivals. Both schedules met every modeled deadline. Earliest-slot dispatch had a 95th-percentile start delay of zero minutes. The forecast policy used the full 60 minutes at that percentile. Total modeled emissions fell from 183.47 to 178.37 g CO2e that day. [Matched daily rows](results.csv?plain=1#L54)

## What does a lookup have to cost to erase the saving?

With one hour of slack, a mixed grid, aligned forecasts and 2 J per candidate lookup, the seven-day saving is 28.10 g CO2e, or 2.33% of baseline emissions including idle allocation. The gross work saving is 33.91 g and the extra 26,169 lookups use 5.81 g. The forecast breaks even at **11.67 J per candidate lookup** under these assumptions. A two-hour phase error makes it emit 36.75 g more than earliest-slot dispatch.

Only three bins in the evaluation period lack observations. The main replay assigns zero arrivals to them, and a second pass assigns the training median of 53. The full results retain both treatments. Real deployment savings would require an issued forecast, measured grid intensity, a service energy measurement and an actual cost for waiting. [Daily replay](results.csv) · [Accounting method](manuscript.md) · [Paper PDF](manuscript.pdf)

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
