# SRC-006 goldfix rescore — round 2 (2026-10-24)

Command (deterministic, no model in the loop):

```
.venv/bin/python evals/score.py --extracted evals/runs/round2 --datasheets ~/datasheets --out /tmp/round2_rescore.json
```

Purpose: record the scoring effect of the same-day 74hc595 gold correction (see
`evals/cases/74hc595_so16/review.md` § "Correction — 2026-10-24"): `lead_length`
`{min: 0.4, max: 1.27}` → `{nom: 1.05}` with the letter-header quote replaced by the nom row,
and the same-day withdrawal of SRC-006's numberless-quote carve-out.

Result against the stored `evals/runs/round2_scores.json`: **12 of 16 runs byte-identical**;
4 runs moved, for two separate, already-adjudicated reasons:

| Run | Field | Stored → rescored | Cause |
|---|---|---|---|
| 74hc595_so16_run1 | dims_ok 8 → 9, dims_wrong `['lead_length']` → `[]` | **today's SRC-006 correction** — both runs had read `nom: 1.05`, which the corrected gold now records |
| 74hc595_so16_run2 | dims_ok 9 → 10, dims_wrong `['lead_length']` → `[]` | same |
| txs0108e_tssop20_run1 | dims_gold 12 → 11, dims_ok 12 → 11, dims_extra +`lead_thickness`, spec_failures +`dim.reference_value`, footprint_identical True → False | **not today's change** — the 2026-10-13 DIM-004 adjudication (`86234b9`) dropped the gold's `lead_thickness`; the stored round-2 scores predate it. Already documented in `evals/runs/dim004_goldfix_rescore.md` |
| txs0108e_tssop20_run2 | dims_gold 12 → 11, dims_ok 11 → 10, dims_extra +`lead_thickness`, spec_failures +`dim.reference_value`, footprint_identical True → False | same |

`usable without edit`: **5/16 before, 5/16 after** (same five runs; the 74hc595 runs stay
unusable on the pin-9 `tri_state` vs `output` symbol disagreement, which no gold change here
touches). quotes_bad moved nowhere: every quote of every run is still on its page, including
the corrected gold quote `mm nom 0.25 1.27 1.05 0.2 0.25 0.1` (a verbatim substring of the
page-15 text layer).

No score was washed: every movement traces to a gold error fixed on rendered-page evidence,
not to a change in what the runs recorded.
