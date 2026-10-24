# Gold review: sn74hc00_soic14

TI SN74HC00 quad 2-input NAND gate, D package (SOIC, 14 pins). Source: `~/datasheets/sn74hc00_soic14.pdf`
(TI SCLS181H, 39 pages, sha256 `e53f9214…`). Only the SN74HC00 was extracted (SN54HC00 shares the sheet;
its numbers live in separate addendum rows and the FK/LCCC column of the pin table) and only the D package.
Package outline: page 23, drawing `D0014A`, "SOIC - 1.75 mm max height", note 5 cites JEDEC MS-012, variation AB.
Example land pattern: page 24, same `D0014A` code. Pin table: page 3, Table 5-1, top view for the
"D, DB, N, NS, PW, J, or W Package".

## KiCad disagreements

Symbol: `/usr/share/kicad/symbols/74xx.kicad_sym`, `74HC00` (extends `74LS00`).
Footprint: `/usr/share/kicad/footprints/Package_SO.pretty/SOIC-14_3.9x8.7mm_P1.27mm.kicad_mod`
(generator `ipc_gullwing_generator.py`, descr cites JEDEC MS-012AB — the same registration the datasheet's
note 5 cites).

| Item | Gold (datasheet) | KiCad | Decision |
|---|---|---|---|
| pin numbers ↔ functions | 1/2/3 = 1A/1B/1Y, 4/5/6 = 2A/2B/2Y, 9/10/8 = 3A/3B/3Y, 12/13/11 = 4A/4B/4Y, VCC 14, GND 7 | same numbers per unit: A(1,2,3), B(4,5,6), C(9,10,8), D(12,13,11), VCC 14, GND 7 | agree, no action |
| pin names | 1A, 1B, 1Y, … from Table 5-1 | gate pins are unnamed (`~`); only VCC/GND named | not a conflict: KiCad draws anonymous gate pins by style; gold keeps the datasheet names (what a board designer reads) |
| electrical types | inputs `input`, outputs `output`, VCC/GND `power_in` | `input` / `output` (some with `inverted` *style* — the NAND bubble, not the type) / `power_in` | agree, no action |
| unit grouping | groups `1`–`4` (datasheet's own key: "Channel 1"…"Channel 4") | units A–D (KiCad's letters) | keys differ by source; reference.md mandates the datasheet's key, so gold uses `1`–`4` |
| pitch | 1.27 | 1.27 | agree |
| body_length | 8.55–8.75 (mid 8.65) | F.Fab 8.65 | agree (within range, mid exact) |
| body_width | 3.8–4.0 (mid 3.9) | F.Fab 3.9 | agree |
| `land_pad_length` | **1.55** (TI, parenthesised) | **1.95** | disagree → keep TI: the gold records the datasheet's own example land pattern |
| `land_span` | **5.4** (TI, parenthesised) | **4.95** (pads at x = ±2.475) | disagree → keep TI, same basis |
| `land_pad_width` | 0.6 | 0.6 | agree |
| `overall_width` 5.8–6.2 | — | no 2D counterpart (courtyard ±3.7 = 7.4 is a margin, not a measured tip-to-tip) | no comparison possible |
| height/standoff/lead_length/lead_thickness | from outline | not carried in the 2D footprint (3D-model domain; MS-012AB consistent) | no comparison possible |

The land-pattern disagreement is real but benign: TI's `D0014A` example (pads 1.55 × 0.6, rows 5.4 apart)
and KiCad's IPC-7351 nominal gull-wing layout (pads 1.95 × 0.6, rows 4.95 apart) are both valid land patterns
for the same package — the datasheet's own note 6 says "Publication IPC-7351 may have alternate designs".
The gold follows the datasheet because the datasheet is the evidence standard here, not KiCad.

## Values that had to be interpreted

- **standoff (0.10–0.25).** The right-side callout of DETAIL A prints `0.25 / 0.10` with no letter. At 600 dpi
  the upper extension line continues the body underside (pixel row y≈391 at both the body edge and the arrow)
  and the lower line runs level with the foot tip, where the foot's bottom surface touches (y≈447–448) — i.e.
  body underside → seating plane, which is exactly reference.md's standoff span. The nearby boxed
  `0.25 GAGE PLANE` (dash-dot line) was excluded per reference.md's boxed-gage-plane rule.
- **lead_thickness (0.13–0.25, `TYP`).** The side-view callout `0.25 TYP / 0.13`: its two extension lines
  continue the foot's top and bottom surfaces (measured at 300 dpi: surfaces slope 1958→1965 and 1976→1983 px;
  extension lines sit at 1965/1983), so the arrows straddle the lead material itself → thickness, not a gap.
  The `TYP` applies the pair to all 14 leads; the two stacked numbers give max over min.
- **lead_length (0.40–1.27).** DETAIL A's horizontal arrows run between the vertical extension line at the lead
  tip (x≈605 at 600 dpi) and the one dropping from where the flat underside starts to rise into the bend
  (x≈765) — tip to start of bend, reference.md's foot span. (The body face lies further right; this is not the
  tip-to-body length, which the sheet does not print and which reference.md excludes.)
- **overall_width (5.8–6.2).** Top-left callout `6.2 TYP` over `5.8`; its extension lines land on the lead tips
  of both rows (clear of the moulded body edges at 300 dpi) → tip-to-tip across the rows. Read as min/max; see
  the `TYP` oddity under contradictions.
- **pitch (1.27) and the boxed-basic tension.** The callout is `12X` with `1.27` in a box (basic). Reference.md's
  boxed-basic sentence — "a reference plane or a datum, not a size: never record it as `standoff`,
  `lead_length`, `lead_thickness` or anything else" — read literally would exclude it, but its own two
  illustrations (the boxed gage-plane offset that would masquerade as a standoff; a parenthesised lead
  thickness) target values that would be misattributed, while the same reference's letter table maps
  `e` → `pitch` and its example.json records a BSC pitch (`e 0.95 BSC`) as an extracted `nom`. The task brief
  makes reference.md authoritative where the two pull apart: I recorded the pitch (it is the only place the
  sheet states it, and the example endorses exactly this form) and did not extend the same license to the other
  boxed values (`2X 7.62`, `0.25` gage plane), which are recorded nowhere. Tension documented here rather than
  resolved silently.
- **group `power` on GND/VCC.** The pin table's I/O column prints `—` (no `PWR` cell), so reference.md calls
  grouping these two "optional and … equally correct" either way. Grouped `"power"` was chosen: the table's own
  descriptions name them "Ground" / "Positive Supply", common to all four channels.

## Deliberately left out

- `2X 7.62` (boxed): a lead centre-to-centre span — reference.md excludes spans, and it is basic.
- Boxed `0.25 GAGE PLANE` (DETAIL A) and boxed `0.1 C` profile (top view, seating plane): gage-plane/datum
  material, not sizes; explicitly not a standoff.
- `⌖ Ø0.25 Ⓜ C A B` position-tolerance feature control frame: GD&T tolerance, not a dimension.
- `0° –8°`: lead bend angle — the dimension vocabulary has no name for it.
- `(R0.05) TYP`: land-pad corner radius — no dimension name.
- `0.07 MAX / 0.07 MIN ALL AROUND` (solder mask details): mask, not metal — reference.md records mask openings
  never, and here even the metal callouts are present, so nothing is substituted.
- Notes 3/4 allowances (mold flash 0.15 mm, interlead flash 0.43 mm per side): tolerance notes, not callouts.
- Pin 1 ID area: hatched, no dimension printed for it on this drawing.
- Nothing was recorded from the DB/N/NS/PW outline pages (28, 33, 36) or the FK/LCCC pin column — different
  packages; the D column of Table 5-1 and the top view supply every D-package pairing.
- No `alt_names` anywhere: no pin on this part has a second function; the FK column's numbers share table rows
  with the D numbers but are a sibling package's pinout, not alternate functions (reference.md's sibling rule).

## Contradictions inside the datasheet

- **`6.2 TYP` over `5.8`.** A `TYP` qualifier sits on the top value of a stacked pair; TYP and a min/max pair
  are different readings, and the sheet prints no letter for this callout. JEDEC MS-012AB (note 5's own
  registration) gives E = 5.80–6.20 MIN/MAX, so the pair was read as min/max. Recorded 5.8/6.2.
- **`12X 1.27` (and the land pattern's `12X (1.27)`).** Fourteen leads in a row make thirteen pitch intervals,
  but both sheets print the multiplicity as 12X. TI's own count, repeated on both drawings; the value (1.27) is
  what matters and matches JEDEC `e`. Recorded with the quote as printed.
- **Lead thickness vs JEDEC.** The side view prints 0.13–0.25 while note 5 cites JEDEC MS-012AB, whose `c`
  minimum is 0.10 — the sheet's own drawing is stricter than the standard it references. The drawing governs;
  0.13–0.25 recorded. (DETAIL A's other vertical callout, 0.10–0.25, is the standoff, so the two ranges
  coexist without conflict.)
- **Addendum status vs revision string.** The PACKAGE OPTION ADDENDUM is dated 18-Sep-2026 while the revision
  is "REVISED AUGUST 2021"; the addendum marks `SN74HC00D` Obsolete and `SN74HC00DR` Active. See the mpn
  paragraph — this affects which orderable is "current", not the extraction.

## Coverage of the verification

- **Pins.** All 14 pairings verified twice: Table 5-1 rows and the rendered top view (300 dpi crop of page 3;
  left column 1A–GND top-to-bottom, right column VCC–3Y top-to-bottom, matching). Types from the I/O column.
  Three-state check: the sheet's only high-impedance text is §8.4 "Standard CMOS Inputs … are high impedance"
  — about inputs; no output Z state and no OE pin exists, so the four Y pins stay `output` (the 74HC595
  counter-example in reference.md does not apply to this part). GND/VCC typed `power_in` through the supply
  rule → `inferred`; the twelve signal pins are `extracted`.
- **Outline (page 23).** Rendered at 110, 300, 400 and 600 dpi; seven callout regions cropped and every
  extension line traced: `6.2 TYP/5.8` (tips), `A 1.75 MAX` (side view), `8.75/8.55 NOTE 3` (body along rows),
  `4.0/3.8 NOTE 4` + datum B (body across), `12X 1.27` (adjacent pin centrelines), `14X 0.51/0.31` (one lead's
  width), DETAIL A's three callouts (standoff, foot length, and the boxed gage plane). Where callouts sit
  within a few pixels the decision was made by measuring pixel rows of the lines at fixed columns, not by eye
  (standoff: body edge y≈391 vs arrows' lines y≈391/448; seating plane level with the foot tip y≈447).
- **Land pattern (page 24).** Rendered at 110 and 300 dpi. `14X (1.55)` arrows span the pad's long (row)
  direction, `14X (0.6)` its across direction, `12X (1.27)` spans adjacent pad centrelines, and `(5.4)` runs
  from the left row's centreline (through pad 7) to the right row's centreline (through pad 8) —
  centre-to-center, as `land_span` is defined. All three recorded as one set.
- **Quotes.** Built from `pdftotext -layout` (the checker's own extraction), then pre-tested mechanically
  against the whitespace-normalised page text; every quote in the gold matches contiguously. Where the layout
  interleaves neighbouring callouts into the same lines (the page's own token order, what the validator's
  hint would suggest), the stretch quoted carries both recorded values and the interlopers are listed here:
  `overall_width` quote passes through the side view's `SEATING PLANE` words (no numbers); `body_length`
  carries the boxed `2X 7.62` tokens; `body_width` carries `0.31` (lead-width min) and `1.75 MAX` (height)
  plus this callout's own datum flag `B`; `lead_width` carries `4.0` (body-width max); `standoff` carries
  `0 -8` and `1.27`; `lead_length` carries `0.10`. None of those stray numbers is recorded under the
  dimension the quote anchors; the rendered-image evidence, not the token stream, is what assigned each callout.
- **No `confirmed` anywhere:** only a human confirms; the two supply pins are the only `inferred` entries.
- **mpn** — see below.

## mpn

Page 1's Device Information table prints `SN74HC00D` for "SOIC (14), 8.70 mm × 3.90 mm" — the datasheet's own
canonical part number for this package. The PACKAGE OPTION ADDENDUM lists, for SOIC (D) | 14: `SN74HC00D`
(Obsolete), `SN74HC00DR` (Active, tape and reel), `SN74HC00DR.A`, `SN74HC00DRG4`, `SN74HC00DRG4.A`,
`SN74HC00DT` (Obsolete). reference.md: the mpn is the addendum's orderable, suffix and all, but a tape-and-reel
suffix is dropped "only when the page prints the shorter number" — and page 1 prints `SN74HC00D`. Gold:
**`SN74HC00D`** — printed on a page, an addendum orderable, the base orderable of the package this case
targets. If the active orderable is preferred instead, that is `SN74HC00DR`; the tension between "suffix and
all" (→ DR) and "drop the reel suffix when the shorter number is printed" (→ D) resolves to the shorter form
because the rule's condition is met on page 1 itself. Manufacturer string "Texas Instruments" as printed.
