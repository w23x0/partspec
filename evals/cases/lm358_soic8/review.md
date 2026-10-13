# Review — LM358DR, TI SOIC-8 (D0008A), datasheet SLOS068AB

Round-1 GOLD-verdict import, no review at the time. This file was created 2026-10-14 to record
the one adjudication the MPN-001 round needed.

## MPN (fixed 2026-10-14, `[GOLD]`)

`LM358` → `LM358DR`. The old value was the device name. Two earlier reviews
(`lm358_soic8` readers, via `ne555_soic8` and `tlc555_soic8`) had deferred to a shared premise —
"LM358 is orderable without a package suffix" — and a mechanical check disproved it: TI's PACKAGE
OPTION ADDENDUM lists every orderable with a package/carrier suffix and no bare `LM358` row, and a
token-boundary search of all 34-pages-of-prose finds `LM358` only as the device name.

The ordering table (p.39) prints for this case's package:
`LM358DR  Active  Production  SOIC (D) | 8  2500 | LARGE T&R`.

Other rows on the same tables are other grades/variants (`LM358ADR` temperature grade, `LM358BIDR`
accuracy grade B, `LM358DR.A/.B`, `LM358DRG4`), other packages (`LM358BAIDR` for the other SOIC
row is a B-grade), and sibling parts (`LM258`, `LM2904`) that share the sheet. MPN-001 and
`reference.md`'s mpn paragraph take the addendum's orderable; the "no orderable printed" escape
clause does not apply. The symbol Value changes accordingly; nothing else in the spec is affected.
