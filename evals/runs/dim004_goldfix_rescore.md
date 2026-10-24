# DIM-004 gold fix: rescore of the affected rounds (2026-10-13)

The 2026-10-13 `[GOLD]` fix (commit 86234b9) deleted `lead_thickness` from
`txs0108e_tssop20`, `sn74lvc2t45_vssop8` and `pca9306_vssop8` — the recorded value was the
drawing's parenthesised (reference-only) thickness callout, which DIM-004 and `reference.md`
forbid as a package dimension. Per the gold protocol the affected rounds were rescored with the
fixed golds; the recorded `*_scores.json` files are untouched, this report is the delta.

```
.venv/bin/python evals/score.py --extracted evals/runs/<round> --out /tmp/rescore/<round>.json
```

| round | run | dims before | dims after | usable before | usable after |
|---|---|---|---|---|---|
| round2 | txs0108e_tssop20_run1 | 12/12 | 11/11 | no | no |
| round2 | txs0108e_tssop20_run2 | 11/12 | 10/11 | no | no |
| round4 | pca9306_vssop8_run1 | 11/12 | 11/11 | no | no |
| round4 | pca9306_vssop8_run2 | 12/12 | 11/11 | YES | no |
| round5 | sn74lvc2t45_vssop8_run1 | 9/12 | 9/11 | YES | YES |
| round5 | sn74lvc2t45_vssop8_run2 | 5/12 | 5/11 | YES | YES |

Every other run in the three rounds is byte-for-byte unchanged, and no other case's numbers moved.

Reading of the deltas — the direction is forced by the rule, not chosen to flatter anyone:

- The golds lose one dimension each (12 -> 11), so a run that recorded `lead_thickness` no longer
  gets a match for it; the remaining dims_ok hold.
- pca9306_run2 is the one run whose status flips: it had recorded the parenthesised `(0.13) TYP`
  and matched the old gold exactly. With the fixed gold that value is an *extra* dimension, so the
  run is no longer usable without edit. The flip is the rule doing its job: the run recorded a
  value DIM-004 now rejects.
- No run gains from the change, and the quote layer is untouchable here (no datasheets in this
  repo), so quotes stay unscored (`-`) exactly as in the recorded runs.
