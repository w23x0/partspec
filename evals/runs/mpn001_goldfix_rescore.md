# MPN-001 gold fix: rescore of the recorded rounds (2026-10-14)

The 2026-10-14 `[GOLD]` fix (this round) changed thirteen gold `mpn` values from device names or
wildcard forms to the printed orderable (`ADS1115IDGSR`, `LM358DR`, `MCP23008T-E/SO`, …; the
per-case citations are in each `review.md`). Per the gold protocol the recorded rounds were
rescored against the fixed golds:

```
.venv/bin/python evals/score.py --extracted evals/runs/<round> --datasheets ~/datasheets --out /tmp/rescore_<round>_ds.json
```

**Result: no score movement is attributable to the mpn change.** `evals/score.py` and
`src/kicad_partspec/scoring.py` never compare `mpn` (confirmed by grep); the fields that did move
are all the 2026-10-13 DIM-004 gold fix and its new `dim.reference_value` checker surfacing
against the historical score files (which predate both).

| round | run | field | recorded | now | cause |
|---|---|---|---|---|---|
| round2 | txs0108e_tssop20_run1/run2 | spec_failures | [] | `dim.reference_value` | run recorded the parenthesised `(0.15) TYP` lead_thickness; the 10-13 checker now fails it (yesterday's `dim004_goldfix_rescore.md`, extended here) |
| round4 | uln2003a_tssop16_run2 | spec_failures | [] | `dim.reference_value` | same; this run was not in yesterday's table |
| round4 | pca9306_vssop8_run2 | spec_failures, dims_*, symbol/footprint, usable | 12/12, YES | 11/11, no | same, as yesterday's table recorded |
| round4 | pca9306_run1 | dims_gold, dims_missing | 12 | 11 | same |
| round5 | sn74lvc2t45_run1/run2 | dims_* | 12 | 11 | same |
| round2/4/5 | all runs of the other 14 cases | — | — | identical | mpn not scored |

`symbol_identical`/`footprint_identical` go False whenever `spec_failures` is non-empty
(`scoring.py:183-189` only sets them for a clean spec), which is why the DIM-004 finding also
takes `usable_without_edit` down for the three affected runs. That is the rule working as
intended: those runs recorded a value the spec layer now rejects.

The historical `*_scores.json` files are left untouched; this report is the delta record.
