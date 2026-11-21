# Preparation record

How much energy can a carbon-aware scheduler spend evaluating a later start?

Vedant Thaker · 21 November 2026

## Original work

Vedant Thaker is the sole author. He designed the original carbon-aware scheduling study, wrote its manuscript, developed its original software, and requested the comparisons and checks reported in this revision.

The author reports that the research project began on 2 August 2026. The previous versions and the new revision represent different stages of the work.

## Revision activities

OpenAI Codex assisted with the scheduling replays, preparation of the trace-based comparisons, accounting and time-boundary checks, and source verification, as well as literature checks and preparation of the revised text. The author set the research question and requested the revision.

## Computational checks

A separate event sweep checked the candidate decisions saved for both 60-minute previous-day replays, the multiset of eligible allocations, allowed delays, node peaks, integrated job attribution and break-even values. Raw source digests and transformations are listed in DATA-SOURCES.md. The legacy verifier checked the count digest and energy arithmetic. A fresh calculation matched all legacy scenario keys and integer fields, with maximum absolute floating-field difference below 6 × 10⁻¹⁴.

## Data and version records

The accompanying supplement includes the dated UK allocation subsets, GB intensity, meter percentiles, reservation audit, both weeks’ outputs and source hashes. DATA-SOURCES.md identifies the inputs, attribution and transformations. Run python dated_replay.py and python check_dated.py, then repeat both commands with --repeat. All four runs use standard Python. The original count replay, upstream data notice and 1,008 daily rows are available in the baseline repository. Environment locks, run.py, verify.py, a row comparator and the continuous-week replay accompany that experiment.

[Original pinned software](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/dea2cea99bfc52fb21a7321fdc0d676060e5472d) · [Revision code and data](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/main/revision/supplement)

The reported checks are computational. No independent personal rerun or line-by-line review of these revisions by the author is asserted here.
