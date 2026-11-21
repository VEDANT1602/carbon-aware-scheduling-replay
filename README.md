# How much does a one-hour deferral change the carbon account of a compute queue?

Technical report by Vedant Thaker, Independent Researcher, Jeffersonville, Indiana. Correspondence: vedant.thaker1602@gmail.com.

An HPC dispatcher deciding whether to wait must choose before it knows the job’s duration or the future grid intensity. We replayed 76,765 dated ARCHER2 job starts across two weeks in March 2022. A capacity-limited dispatcher compared the previous day’s grid intensities at three possible start times and otherwise used first-in, first-out service. In a scenario where every job of at most four nodes could wait for up to an hour, estimated compute emissions for all released jobs fell by 50.33 kg (0.092%) in week one and 17.83 kg (0.024%) in week two. Mean additional wait across the full job population was 21.8 and 26.9 minutes. Two and five nonparticipants also waited for capacity. Small gross changes in a retrospective carbon account leave open whether the service would save energy or emissions after accounting for controller overhead, unrecorded site constraints and users’ delay preferences.

- [Read the paper](manuscript.pdf)
- [Read the plain-text manuscript](manuscript.md)
- [Reproduce the analysis and inspect the source and data records](study/README.md)
- [Software license](LICENSE) and [third-party terms](LICENSING.md)
- [Preparation record](study/PREPARATION.md)
- [Previous manuscript and supplements](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/a31ba8a660c26067dddd8121c313332d9939a89b)
