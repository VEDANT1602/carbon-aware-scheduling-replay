# The carbon opportunity in one hour of flexibility at ARCHER2

Scheduling study by Vedant Thaker, Independent Researcher, Jeffersonville, Indiana, USA. Revised November 24, 2026.

ARCHER2 publishes job starts but records neither submission times nor permission to defer jobs in this dataset. We use its observed starts to ask a narrower question: how much national-average compute carbon could three start choices have changed? Eight weeks from March through September 2022 cover 292,776 allocations. For jobs with up to four nodes we allowed delays of zero, 30 or 60 minutes and kept other starts fixed. A four-week same-weekday signal yielded a modeled saving of 204.23 kg CO₂ (0.0313% of all-job compute emissions), against 116.09 kg for the previous-day signal. Letting each job draw a fixed power within the central half of the March meter distribution gave a pooled four-week-signal saving of 101–289 kg across extreme assignments. A feasible schedule with perfect information saved 1,001.99 kg. Relaxing capacity raised the upper bound to 1,017.09 kg (0.1559%). This bounds the opportunity within the assumed start choices and constant-power account.

[Paper (PDF)](manuscript.pdf) · [Editable text](manuscript.md) · [Methods and study files](study/README.md) · [Manuscript history](study/VERSION.md)

[Author-owned software license](LICENSE) · [Third-party terms](LICENSING.md) · [Previous version](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/e5b3039b2c8aba1695f08a9bef441d31d65950c0)
