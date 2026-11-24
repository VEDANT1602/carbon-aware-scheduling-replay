# Preparation record

The research question and author-supplied disclosures are attributed to Vedant Thaker. The public working version dated 21 November 2026 records new analysis undertaken in response to his study-specific critique. The methods, results and source checks were prepared with assistance from OpenAI Codex. The byline identifies the human author. This record does not certify independent personal inspection, peer review, or final submission approval.

An independent cumulative-intensity calculation and an event sweep reproduced the gross weekly differences and peak occupancies. The immediate-start policy recovered each of the 76,765 recorded release-cohort starts exactly. These checks establish numerical consistency within the release-time queue model.

The supplement README identifies the inputs and computations needed to inspect the numerical results. Earlier public material is retained at https://github.com/VEDANT1602/carbon-aware-scheduling-replay/tree/a31ba8a660c26067dddd8121c313332d9939a89b .

## Current work

Vedant Thaker is the sole author. He specified the scheduler comparison, including the need to distinguish forecasting error from limited flexibility. OpenAI Codex assisted with the replay and oracle implementations, numerical checks, source checks and drafting.

On November 22, 2026, the comparison was extended at the author's request to the first Monday week of nine calendar months and the second original March week. Checks on original capacity ruled out two conflicting calendars. Past-only day, same-weekday and four-week-mean signals were replayed for the other eight, and their all-job baselines and perfect-information ceilings were independently recalculated by direct half-hour integration.

## Date verification on November 22, 2026

The author reports September 19–October 1, 2026 for the original work. The earliest public commit follows the end of the author-reported interval. Work during that interval cannot be verified from this history. The [first PDF commit](https://github.com/VEDANT1602/carbon-aware-scheduling-replay/commit/01da64f9a7bd3ba6a6ffc9521fbacc4927f3383b), the November 20 review copy, and the November 21 and 22 manuscript versions are recorded separately in [the manuscript history](VERSION.md).


November 24, 2026. Codex implemented the paired job-power sensitivity calculation in response to the review of the common power assumption, reconstructed the protected schedules, and revised the interpretation. Each job keeps one power across the two counterfactual starts. The new analysis is retrospective. No individual job power or scheduler energy was measured for this revision.

## November 24 editorial work

Vedant Thaker supplied the critique and requested this revision. OpenAI Codex assisted with the analysis checks and revised prose. The manuscript describes the study-specific work and its limitations.
