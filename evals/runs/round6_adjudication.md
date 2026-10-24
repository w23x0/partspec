# Round 6 adjudication — 2026-10-24

One adjudicator agent per case, on the PDF text and 150–1200 dpi renders, deciding every scored
disagreement against SKILL.md and reference.md (verdicts GOLD / RUN / BOTH / NEITHER), plus a full
independent audit of the gold itself. Sections follow, concatenated verbatim.

Note: in the lm393b section the narrative's run1/run2 attribution was cross-checked against the
run files before assembly — run1 matches the gold on both contested dimensions (12/12); run2 is
the swapped reading the scorer flagged.

---

# Adjudication — lm393b_soic8 (extraction round 6)

Datasheet: `~/datasheets/lm393b_soic8.pdf` (TI SLCS005AH, 56 pages), sha256
`f28830c2f4cbd9ef6a1cd6788a840fa2b92caafee366d53385f88d1cf24e9456` (recomputed, matches gold).
Pages used as evidence: 1 (title/revision), 3 (Fig 4-1 + Table 4-1), 26 (orderable addendum),
43 (PACKAGE OUTLINE D0008A), 44 (EXAMPLE BOARD LAYOUT D0008A). Renders: whole pages at 150 dpi;
page 43 regions at 600 dpi; DETAIL A halves at 1200 dpi; pixel scans of the DETAIL A line work
(blue outline vs black dimension lines distinguished by colour).

Note on the scorer's narrative: it says "run2 read DETAIL A's `.004-.010` as lead_thickness", but the
run files show the opposite assignment — it is **run1** that recorded `lead_thickness` 0.11–0.25 from
`.004-.010` and `standoff` max 0.1 from `.004 [0.1] C`, while run2 matches the gold on `lead_thickness`
and differs from it on `standoff` only in quote and status (same values 0.11–0.25). The files are
authoritative; this adjudication settles the items as the files record them.

---

## 1. Contested item: `standoff`

| Source | Record |
|---|---|
| gold | min 0.11, max 0.25, page 43, quote `.004-.010`, status extracted |
| run1 | max 0.1, page 43, quote `.004 [0.1] C`, status inferred |
| run2 | min 0.11, max 0.25, page 43, quote `[0.11-0.25]`, status inferred |

**Verdict: GOLD.**

Evidence (page 43, DETAIL A, traced at 600 dpi and 1200 dpi):

- The `.004-.010 [0.11-0.25]` callout's two arrows sit at the far right of DETAIL A. The upper arrow
  points down and its tip touches a horizontal line at y≈668 (600 dpi crop coordinates) that is
  collinear with the blue moulded-body bottom edge (blue line y 666–670, x 1180–1417, continued
  rightward across the wavy break as the black extension line, x 1450–1648). The lower arrow points up
  and its tip touches the long solid line at y≈722–724 (x 944–1648) that is collinear with the lead
  foot's bottom resting edge — the seating plane (the same plane the `0°-8°` foot-tilt angle is
  measured against, and the plane labelled SEATING PLANE / datum C in the main view). The dimension
  therefore spans **body underside ↔ seating plane** — exactly the reference's `standoff` row
  ("the body underside and the seating (gage) plane | `standoff`"). The gold review's pixel-trace claim
  is confirmed independently.
- The dashed horizontal line at y≈645 (23 px above the body underside) is a *different* callout: it is
  the target of the boxed `.010 [0.25]` (whose arrow pair spans y 645 → 722, i.e. seating plane to
  dashed line), and it pairs with the position feature control frame `⌖ .010 [0.25] Ⓜ C A B` in the top
  view. The dashed value (0.25) equals the *max* of the `.004-.010` standoff range — the two callouts
  cohere as the GD&T basic + tolerance pair, and neither is a second thickness.
- Run1's `standoff` source `.004 [0.1] C` is the **gage-plane offset**: rendered at 600 dpi (top right
  of page 43), its arrows span between the seating-plane line (datum C, the long vertical line the
  SEATING PLANE label and the boxed `C` datum symbol point at) and the dashed gage-plane line at the
  lead tips. The reference forbids this explicitly: "A boxed basic dimension, or one labelled GAGE
  PLANE, is a reference plane or a datum, not a size: never record it as `standoff`…". Run1's record
  is wrong in callout, value (0.1 vs the true 0.11–0.25 range) and it leaves the real standoff callout
  misassigned to `lead_thickness` (item 2).
- Run2's values and callout attribution are correct; quoting only the millimetre bracket `[0.11-0.25]`
  (which is on the page and carries both recorded values) with status `inferred` is rule-compliant
  ("An `inferred` dimension is a marked interpretation; the checker does not test it"), but the gold's
  record — the inch token of the very callout, marked `extracted` after the pixel-level span
  verification — is the stronger, correct form.

Correction to apply: none (gold stands).

---

## 2. Contested item: `lead_thickness`

| Source | Record |
|---|---|
| gold | min 0.13, max 0.25, page 43, quote `.005-.010 TYP [0.13-0.25]`, status extracted |
| run1 | min 0.11, max 0.25, page 43, quote `.004-.010`, status extracted |
| run2 | identical to gold |

**Verdict: GOLD** (run2 agrees with the gold; run1 is wrong).

Evidence (page 43, side view, 600 dpi crop `sideview`): the `.005-.010 TYP [0.13-0.25]` callout's two
arrows — one descending from above, one ascending from below — touch two thin parallel extension lines
that continue the **top and bottom surfaces of one lead seen edge-on** where it extends beyond the
body in the side view. That is "the two edges of one lead's cross-section, in the front or side view"
→ `lead_thickness`, with `TYP` supplying the nom-form for all leads (here a range, so min/max).
The reference's anti-contradiction logic also decides it: DETAIL A's `.004-.010` is the standoff
(item 1), and one lead cannot carry two different thickness ranges (0.11–0.25 and 0.13–0.25); only the
side-view `.005-.010 TYP` straddles the lead material, so it alone is the thickness. Run1's use of the
DETAIL A callout for thickness is a misreading of the extension lines (the arrows it quotes sit far
right of the foot, between the body-underside line and the seating plane, not across the lead).

Correction to apply: none (gold stands).

---

## 3. run1 — residual deltas from gold (not in the scored disagreement set)

All of run1's other differences from the gold are quote-style variants that pass the quoting rules —
each quote is a token sequence on the cited page and carries the recorded values:
`body_length` `[4.81-5.00]`, `body_width` `[3.81-3.98]`, `overall_width` `.228-.244 TYP [5.80-6.19]`,
`height` `[1.75]`, and pin quotes that add the DESCRIPTION column text (`GND 4 4 — Ground`,
`VCC 8 8 — Positive Supply`, etc.; whitespace/line-break-insensitive match, on page 3). Values,
statuses, groups and types are identical to the gold on every one of these. Run1's only substantive
errors are the two contested items above (its `standoff` and `lead_thickness` are both wrong). Its
`datasheet.revision` `"SLCS005AH"` is shorter than the page-1 string but not false; gold's fuller
string is the better copy.

## 4. run2 — residual deltas from gold (not in the scored disagreement set)

Run2 differs from the gold only in `standoff`'s quote (`[0.11-0.25]` vs `.004-.010`) and status
(`inferred` vs `extracted`) — same callout, same values. Rule-compliant (see item 1); the gold's form
is the better evidence. Everything else in run2 matches the gold (its pin quotes add the on-page
DESCRIPTION text and explicit `alt_names: []`, both permitted).

---

## 5. Independent gold audit — pins (page 3, Fig 4-1 verified on the 150 dpi render)

Pairing 8/8 on the rendered figure: 1OUT=1, 1IN−=2, 1IN+=3, GND=4 down the left; VCC=8, 2OUT=7,
2IN−=6, 2IN+=5 down the right. Table 4-1 rows match the gold quotes token-for-token (en dash U+2013 in
`1IN– 2 2 Input`, ASCII hyphen U+002D in `2IN- 6 6 Input` — codepoints verified; gold *names*
normalize to the ASCII hyphen per the skill). The Thermal Pad row and Fig 4-2 (`V+`, `PAD`) belong to
the DSG/WSON package and are correctly absent from names and `alt_names`.

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | pin 1 `1OUT`, open_collector, group 1, inferred, quote `1OUT 1 1 Output` | GOLD | Table 4-1 row on page 3; type: prose §6.1 "The open-collector outputs allow the user to level shift…" (found in the text layer) → reference's open-collector row, status inferred |
| 2 | pin 2 `1IN-`, input, group 1, extracted, quote `1IN– 2 2 Input` | GOLD | Table 4-1 row; I/O column "Input"; dash codepoints as printed; name normalized per skill |
| 3 | pin 3 `1IN+`, input, group 1, extracted, quote `1IN+ 3 3 Input` | GOLD | Table 4-1 row |
| 4 | pin 4 `GND`, power_in, group power, inferred, quote `GND 4 4` | GOLD | Table 4-1 row (I/O column prints "—"); ground pin → `power_in` inferred per reference type table |
| 5 | pin 5 `2IN+`, input, group 2, extracted, quote `2IN+ 5 5 Input` | GOLD | Table 4-1 row |
| 6 | pin 6 `2IN-`, input, group 2, extracted, quote `2IN- 6 6 Input` | GOLD | Table 4-1 row (ASCII hyphen as printed) |
| 7 | pin 7 `2OUT`, open_collector, group 2, inferred, quote `2OUT 7 7 Output` | GOLD | Same treatment as pin 1 |
| 8 | pin 8 `VCC`, power_in, group power, inferred, quote `VCC 8 8` | GOLD | Table 4-1 row ("Positive Supply") |
| 9 | Grouping scheme: units `1`/`2`, supplies `power` | GOLD | Two identical comparators → grouping mandatory; keys are the datasheet's own unit names ("comparator 1/2") → `1`/`2`. VCC/GND are the shared rails common to all units → `power` taken in addition, per the reference's supply exception. The "optional power" clause is for lone supplies on parts with no unit groups — not this part. |

## 6. Independent gold audit — dimensions

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 10 | `pitch` nom 1.27, `6X .050 [1.27]`, p43, extracted | GOLD | Top view, boxed basic callout between the pin 8 / pin 7 centerlines (verified at 600 dpi: `.050` and `[1.27]` drawn boxed); boxed pitch ≈ BSC → `nom`; the reference excludes boxed *gage-plane/position* basics, not the `e` pitch |
| 11 | `body_length` 4.81–5.00, `.189-.197`, p43 | GOLD | Top view, along the pin rows, extension lines on the moulded body edges (leads exit left/right only, so nothing protrudes along the rows); NOTE 3; bracketed mm as printed |
| 12 | `body_width` 3.81–3.98, `.150-.157`, p43 | GOLD | Top view, B-datum dimension across between the rows, on body edges (not lead tips); NOTE 4 |
| 13 | `overall_width` 5.80–6.19, `.228-.244 TYP`, p43 | GOLD | Extension lines verified at 600 dpi to land outside the body edges, on the left-row and right-row **lead tips** (tip-to-tip across the rows) → `overall_width` per the reference; inch quote supports the values once converted (TI's own bracket `[5.80-6.19]` is on the drawing); `TYP` as printed |
| 14 | `height` max 1.75, `.069 MAX`, p43 | GOLD | Rotated end view: horizontal dimension from the seating-plane line to the package top (verified at 600 dpi) → overall height above the board, MAX → max only |
| 15 | `lead_width` 0.31–0.51, `8X .012-.020`, p43 | GOLD | Top view, each lead's cross-section width, 8X count = 8 leads; sits with the `⌖ .010 [0.25] Ⓜ C A B` position FCF |
| 16 | `lead_length` 0.41–1.27, `.016-.050 [0.41-1.27]`, p43 | GOLD | DETAIL A foot row: tip → start of the bend, the flat resting foot — the reference's exact `lead_length` span; matches the sibling golds on the same drawing (ne555 p30, tlc555 p38, lm358 p54, ina219 p33) |
| 17 | `standoff` (contested, item 1) | GOLD | See section 1 |
| 18 | `lead_thickness` (contested, item 2) | GOLD | See section 2 |
| 19 | `land_pad_length` nom 1.55, `8X (.061 ) [1.55]`, p44 | GOLD | Horizontal pad extent along the lead direction on the exposed metal (render at 150 dpi: arrows span pad 1 horizontally); parenthesized reference values are explicitly permitted for `land_*`; quote reproduces the printed space `(.061 )` |
| 20 | `land_pad_width` nom 0.6, `8X (.024) [0.6]`, p44 | GOLD | Vertical pad extent on the same exposed-metal pads |
| 21 | `land_span` nom 5.4, `(.213) [5.4]`, p44 | GOLD | Between the two dash-dot pad-column centerlines (center-to-center per the reference), on the metal; the three land dims are recorded as one complete set |

## 7. Independent gold audit — metadata, package header, omissions

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 22 | `mpn` LM393BIDR; manufacturer "Texas Instruments" | GOLD | Page 26 addendum row: `LM393BIDR / Active / Production / SOIC (D) / 8 / 2500 / LARGE T&R`; the `.A`/`.B`/`G4` rows share the base number and no page prints a bare `LM393BID`, so the R suffix stays (reference mpn rule) |
| 23 | `datasheet` sha256 / revision `SLCS005AH – OCTOBER 1979 – REVISED APRIL 2025` | GOLD | sha256 recomputed, identical; revision string copied exactly from the page 1 header (en dashes as printed, verified in the text layer) |
| 24 | `family` SOIC, `pin_count` 8, `exposed_pad` false | GOLD | Outline header "SOIC - 1.75 mm max height / SMALL OUTLINE INTEGRATED CIRCUIT"; addendum "SOIC (D) | 8"; Table 4-1 Thermal Pad row is DSG-only (SOIC column prints "—") |
| 25 | Deliberate omissions | GOLD | All correct per the reference: boxed `.010 [0.25]` (DETAIL A basic, pairs with the position FCF — "not a size"), `.004 [0.1] C` (gage-plane offset, never a standoff), `2X .150 [3.81]` (boxed lead centre-to-centre span, "not recorded"), `(.041) [1.04]` (parenthesized reference), `4X (0°-15°)`/`0°-8°` (angles), no `overall_length` callout exists (leads do not protrude along the rows; verified on the top view), no `body_thickness`/A2 callout on D0008A, no `land_ep_size` (no exposed pad), page 44 solder-mask items and `(R.002) TYP [0.05]` are mask/radius, not metal pad sizes |

Cross-checks that support the whole dimension set: JEDEC MS-012 variation AA (NOTE 5) proportions —
body 3.81–3.98 wide × 4.81–5.00 long, 5.80–6.19 tip-to-tip, 1.75 max height; DETAIL A's basic 0.25
equals the top of the standoff range 0.11–0.25, cohering with the `Ⓜ C A B` position tolerance; the
land-pattern tip-to-tip extent (5.4 + 1.55 = 6.95) is consistent with the outline's 5.80–6.19 lead
span plus pad extension, as the gold review already records.

---

## Verdict summary

Every contested item resolves to the gold; the independent audit found no gold defect (every pin,
every dimension, the land set, the `power` grouping on VCC/GND, `mpn` LM393BIDR, and all deliberate
omissions verified against page-cited, render-traced evidence). Run1's two substantive errors are the
misattributed DETAIL A / gage-plane callouts; run2's only variance is a weaker-but-legal
quote/status on `standoff`.

TALLY: GOLD 25 · RUN 0 · BOTH 0 · NEITHER 0

GOLD CORRECTIONS: none

---

# Adjudication — mcp3008_soic16, extraction round 6

Adjudicator's independent verification, performed for this report (all renders and checker runs are new, not taken from the
gold review):

- Datasheet `~/datasheets/mcp3008_soic16.pdf`, sha256 `e6c2231d…` matches `datasheet.sha256` in all three files; 40 pages;
  every footer prints `DS21295D-page N`.
- `pdftotext -layout` whole-document run; pages 15, 20, 32, 33, 37 and 1 additionally rendered (`pdftoppm -r 150`), pages 32
  and 33 re-rendered and cropped at 300 dpi; every contested value read from the 300-dpi crops.
- `kicad-partspec validate --datasheet` re-run on the gold, run1 and run2 (read-only): all three `passed: true`, zero failed
  findings; gold carries exactly 16 `status.inferred` advisories (10 dimensions + 6 pins), run1 19, run2 16.
- Built all three specs with `kicad-partspec build` into scratch dirs and diffed the generated symbols/footprints.
- Decoded the page-32 font glyph map (digits `0`–`9`, `.`) over the checker's own `page_texts` output to bind each byte-garbage
  dimension quote to its exact table row.

Drawing-set catalog (renders, titles read at 150–300 dpi):

| PDF page | Drawing | Package |
|---|---|---|
| 27 | 14-Lead Plastic Dual In-Line (P) – 300 mil Body [PDIP] | MCP3004 |
| 28 | 14-Lead Plastic Small Outline (SL) – Narrow, 3.90 mm Body [SOIC] (C04-065B) | MCP3004 |
| 29 | 8-Lead Plastic Small Outline (SN) – Narrow, 3.90 mm Body [SOIC] (C04-2057A) + its land pattern | **neither device** (page 37 lists no 8-lead SOIC) |
| 30 | 16-Lead Plastic Dual In-Line (P) – 300 mil Body [PDIP] | MCP3008 |
| 31 | 14-Lead Plastic Thin Shrink Small Outline (ST) – 4.4 mm Body [TSSOP] | MCP3004 |
| 32 | 16-Lead Plastic Small Outline (SL) – Narrow, 3.90 mm Body [SOIC] (C04-108B) — package outline | MCP3008 |
| **33** | **16-Lead Plastic Small Outline (SL) – Narrow, 3.90 mm Body [SOIC] (C04-2108A) — RECOMMENDED LAND PATTERN** | **MCP3008** |

Page 33 exists and is the decisive fact of this case: the gold review's repeated claim — "the datasheet's only example land
pattern is on page 29 … 8-Lead (SN)" — is factually wrong. The datasheet has **two** example land patterns; the one on page 33
is for the exact 16-lead SL package the `mpn` MCP3008-I/SL orders (page 37: "b) MCP3008-I/SL: Industrial Temperature, SOIC
package", with `SL = Plastic SOIC (150 mil Body), 14-lead, 16-lead`; page 1: "the MCP3008 is offered in 16-pin PDIP and SOIC
packages"; Table 3-1's MCP3008 "PDIP, SOIC" column carries pins 1–16). Page 29's 8-lead SN figure is the carried-over oddity;
page 33 is not.

---

## 1. run1 — the three `land_*` dimensions

run1 recorded `land_pad_length` max 1.50, `land_pad_width` max 0.60, `land_span` nom 5.40, all sourced to page 33, and
generated `SOIC-16_3.9x9.9mm_P1.27mm` (pads 1.5 × 0.6, rows ±2.7 → 5.4 mm span, pitch 1.27 — verified in the built
`partspec.pretty` output).

### 1a. `land_pad_length` — verdict: **RUN**

Page 33, 300-dpi render of the land-pattern table (drawing C04-2108A): row "Contact Pad Length | Y | – | – | **1.50**" — the
value sits in the MAX column, so `max: 1.50` is exactly the reference's "a value marked MAX gets only `max`" case. Y is the
pad's long axis, pointing radially outward from the silkscreen body — i.e. along the lead direction, the reference's
definition of `land_pad_length`. The gold has no entry; per reference.md ("Take each of these that the datasheet gives") and
SKILL.md ("`land_*` dimensions come only from the datasheet's example land pattern"), the datasheet gives it, so omitting it
is the defect. Run2 omits it for the same (wrong) reason as the gold.

### 1b. `land_pad_width` — verdict: **RUN**

Same table, row "Contact Pad Width | X | – | – | **0.60**" (MAX column): across the row = the reference's
`land_pad_width`. Verified at 300 dpi. Same disposition as 1a.

### 1c. `land_span` — verdict: **RUN**

Same table, row "Contact Pad Spacing | C | – | **5.40** | –" (NOM column). On the 300-dpi figure, C's extension lines are the
**dashed centre-lines through the two pad rows** (8 pads + 8 pads = 16), i.e. centre-to-centre between opposite pad rows —
precisely the reference's `land_span`. Arithmetic corroborates: C = G + Y = 3.90 + 1.50 = 5.40 (G = "Distance Between Pads"
3.90 MIN is the clear gap, not centre-to-centre, so G is not the recordable value; run1 did not record it). `nom 5.40` matches
the NOM column per "a typical value … gets `nom`".

run1 recorded all three pad dimensions together — the reference requires the set "together or not at all" — and marked them
`inferred`, the only consistent status: **page 33's table has no text layer at all** (the whole table is vector art; the
checker's `page_texts` for page 33 contains only the header `MCP3004/3008`, a garbled note line, and the footer), so no
ASCII-digit quote can be built and an `extracted` status would fail SRC-006, exactly as with the gold's page-32 rows.

One quality note, not a defect: run1's quote `"MCP3004/3008"` is the page header. It is on page 33 (checker-verified) and is
in fact the *only* ASCII token on that page, but it names neither the callout nor the value. For `inferred` dimensions the
checker does not test value support; the quote must nonetheless be flagged in the hand-over so a human confirms the values
against the render (as this adjudication does).

---

## 2. run2 — verdict on its shared omission

run2 mirrors the gold: no `land_*` at all, hence `footprint.skipped` and no footprint. Its ten package-outline dimensions are
value-identical to the gold's (each verified below against the render) and its quotes are on-page (`validate` passes; the
doubled pin numbers in quotes like `1 1 CH0 Analog Input` are the MCP3004 sibling column of the same row — on-page, harmless).
Its footprint "matches" in the scorer only because gold and run2 both skip (`_same_footprint` returns true for two skips).
Since the correct record includes the three land dims, run2's omission is wrong for the same reason the gold's is — covered
by verdicts RUN under 1a–1c; no separate correction beyond what the gold correction below implies.

---

## 3. Supply-pin grouping (pins 9 DGND, 14 AGND, 16 VDD) — verdict: **BOTH**

The gold groups all three `"power"`; both runs leave them ungrouped. reference.md's supply bullet governs: *"A lone supply or
ground pin, or a bare printed VDD/VSS pair on a part with no supply block of its own, is neither a unit nor a printed block:
grouping it `"power"` is optional and leaving `group` off it is equally correct."* Table 3-1 (page 15) has no TYPE column and
prints no `PWR` cells anywhere — there is no printed supply block, and DGND/AGND/VDD are lone supply/ground pins. Stated
explicitly: **no gold change and no run correction**; either record satisfies the prose. (CH0–CH7 grouping `"CH0"`–`"CH7"`,
and leaving CS/SHDN, DIN, DOUT, CLK and VREF ungrouped, are required by the prose and done by all three files.)

---

## 4. Generated-symbol difference — attribution

The scorer's `symbol_identical` is a field proxy, not a file diff: it fails when `groups_ok < 16`, and the *only* failing
field for both runs is `group` on pins 9/14/16 (`None` vs `"power"`; names, types and alt_names are 16/16). Both runs'
"symbol differs" flag is therefore caused by the supply-group choice alone.

Building all three specs confirms what the proxy cannot see. In the actual files:

1. **Group structure changes unit placement** (the cause the task anticipated). `gen/symbol.py`'s `unit_groups` makes one unit
   per named group (first-seen order, `"power"` forced last) plus one unit for ungrouped pins. Gold: 10 units — units 1–8 =
   CH0–CH7, unit 9 = the five ungrouped pins (CS/SHDN, DIN, DOUT, CLK, VREF), unit 10 = power (VDD, DGND, AGND). Runs: 9 units
   — unit 9 holds eight pins. Every affected unit's rectangle (`at 0 ±13.97` vs `±16.51`; half-width 5.08 vs 8.89) and each
   pin's coordinates/rotation differ accordingly.
2. **run1 only:** the symbol's `Footprint` property is filled (`"partspec:SOIC-16_3.9x9.9mm_P1.27mm"`) because run1's land
   dims generate a footprint; gold and run2 leave it empty. This is a downstream consequence of disagreement 1, not an
   independent defect.
3. **gold only, both runs affected:** the symbol's `Datasheet` property carries the URL because the gold records
   `datasheet.url`; both runs omit the field, so the property is `""`. This difference is independent of both contested items
   and would survive fixing them; it is provenance metadata, not a pin or dimension error.

Given verdict BOTH on the groups, the group-caused symbol difference is not a defect of either side; given verdict RUN on the
land dims, run1's footprint (and filled Footprint property) is the correct outcome.

---

## 5. Independent gold audit (every pin, every dimension)

All statuses, quotes and groups checked; every value below was re-read from the 300-dpi render of page 32 (drawing C04-108B)
or the 150-dpi renders of pages 15/20/37. `validate` passes for the gold: all 26 quotes found on their cited pages.

### Pins (page 15, Table 3-1, verified on the render; quotes are exact ASCII rows of the MCP3008 "PDIP, SOIC" column)

| Pin | Gold name / type / status / group | Verdict | Evidence |
|---|---|---|---|
| 1–8 | CH0–CH7, `input`, extracted, group CH0–CH7 | **GOLD** | Table 3-1 render: rows 1–8 "CH0…CH7 Analog Input" in the MCP3008 column; direction printed ("Analog Input"), so `extracted` is earned; channel groups use the datasheet's own keys. |
| 9 | DGND, `power_in`, inferred, `power` | **GOLD** | Row "9 DGND Digital Ground"; ground → `power_in` inferred per the mapping table; group `"power"` is the optional choice (verdict BOTH above permits it). |
| 10 | CS/SHDN, `input`, extracted | **GOLD** | Row "10 CS/SHDN Chip Select/Shutdown Input"; direction printed. The printed overline over CS (visible in the render) is recorded as the text layer prints it — cosmetic vs KiCad's `~{CS}`. One compound name → no `alt_names`, per §3.7. |
| 11 | DIN, `input`, extracted | **GOLD** | Row "11 DIN Serial Data In"; direction printed. |
| 12 | DOUT, `tri_state`, inferred | **GOLD** | Row says "Serial Data Out", but page 20 render: Figures 5-1 and 5-2 print **HI-Z** on DOUT while CS is high, and §6.1 says "the output is at high-impedance for the first two clocks" — the 74HC595 rule: a pin the part can put in Z is `tri_state`. |
| 13 | CLK, `input`, inferred | **GOLD** | No direction printed anywhere ("Serial Clock" only); §5.1: "The first clock **received** with CS low … will constitute a start bit", "the device continues to **receive** clocks" — the device receives on this pin, `input`, honestly flagged inferred. |
| 14 | AGND, `power_in`, inferred, `power` | **GOLD** | Row "14 AGND Analog Ground"; same reasoning as pin 9. |
| 15 | VREF, `passive`, inferred | **GOLD** | Row "15 VREF Reference Voltage Input" — the analog-reference row maps to `passive` inferred; §5.1/page-20 note "the reference input becomes a high-impedance node" confirms it is a reference, not a supply. (KiCad's `power_in` is the defensible library choice, but the skill's row is specific.) |
| 16 | VDD, `power_in`, inferred, `power` | **GOLD** | Row "16 VDD +2.7V to 5.5V Power Supply"; same reasoning as pin 9. |

The MCP3004-only cells (pins "5,6 → NC No Connection") are correctly **not** taken — they belong to the sibling part's column.
`alt_names` empty everywhere is correct: Table 3-1 prints exactly one symbol per pin.

### Dimensions (page 32, drawing C04-108B; every value read from the 300-dpi table crop; all `inferred`)

| Name | Gold value | Verdict | Row in the 300-dpi render |
|---|---|---|---|
| pitch | nom 1.27 | **GOLD** | "Pitch e — 1.27 BSC" (NOM column). |
| height | max 1.75 | **GOLD** | "Overall Height A — – – 1.75" (MAX only). |
| body_thickness | min 1.25 | **GOLD** | "Molded Package Thickness A2 — 1.25 – –" (MIN only, recorded as printed; unusual but repeated verbatim on the page-28 14-lead drawing). |
| standoff | min 0.10, max 0.25 | **GOLD** | "Standoff § A1 — 0.10 – 0.25". |
| overall_width | nom 6.00 | **GOLD** | "Overall Width E — 6.00 BSC"; in the plan view E's extension lines land on the lead tips of both rows (tip-to-tip across rows): 6.00 = 3.90 body + 2 × ≈1.05 protrusions, consistent with L1 = 1.04 REF. |
| body_width | nom 3.90 | **GOLD** | "Molded Package Width E1 — 3.90 BSC". |
| body_length | nom 9.90 | **GOLD** | "Overall Length D — 9.90 BSC". The row's printed label says "Overall", but the drawing's geometry governs: D's extension lines land on the moulded body ends (a SOIC's leads protrude only on the two long sides, so no tip-to-tip-along-rows callout exists), note 3 groups D with E1 as moulded-body dimensions, and the skill's letter table maps `D` → `body_length`. `overall_length` is rightly absent rather than a renamed body dim. |
| lead_length | min 0.40, max 1.27 | **GOLD** | "Foot Length L — 0.40 – 1.27" — the foot from tip to bend, the skill's `lead_length`. |
| lead_thickness | min 0.17, max 0.25 | **GOLD** | "Lead Thickness c — 0.17 – 0.25". |
| lead_width | min 0.31, max 0.51 | **GOLD** | "Lead Width b — 0.31 – 0.51". |

All ten correctly `inferred`: the page-32 text layer has no ASCII digit, so no quote can carry the value and `extracted`
would fail SRC-006. The byte-exact garbage-row quotes were independently bound to their rows by decoding the font glyph map
(digits `0`–`9`, `.`) over the checker's own page text: each quote's decoded value sits in the correct row and column (pitch →
`1.27 BSC`; D → `9.90`; E1 → `3.90`; E → `6.00`; A → MAX `1.75`; A2 → MIN `1.25`; A1 → `0.10/0.25`; L → `0.40/1.27`;
c → `0.17/0.25`; b → `0.31/0.51` — trailing `1`s vanish only under whitespace normalization because the glyph for `1` is
`\x1d`, the artifact the review documents). No quote names a different callout.

### Deliberate exclusions and provenance

| Item | Verdict | Evidence |
|---|---|---|
| `h` chamfer 0.25–0.50 excluded | **GOLD** | No chamfer name in the skill's dimension list. |
| `L1` "Footprint" 1.04 REF excluded | **GOLD** | REF dimension, and body-face-to-tip — the callout the skill says is *not* `lead_length`. |
| φ/α/β angles excluded | **GOLD** | Angles; no names. |
| `overall_length` absent | **GOLD** | No tip-to-tip-along-rows callout exists (verified in the plan view); skill says leave it out. |
| MCP3004 cells / NC row not taken | **GOLD** | Sibling-part columns; reference's multi-part rule. |
| `mpn` = MCP3008-I/SL | **GOLD** | Page 37 render, example b): "MCP3008-I/SL: Industrial Temperature, SOIC package." Tape-and-reel MCP3008T not used, per the reference's suffix rule. |
| revision DS21295D / sha256 / manufacturer / `exposed_pad: false` / family SOIC | **GOLD** | Footers on every page; hash matched locally; "© 2008 Microchip Technology Inc."; 16-lead SOIC has no exposed pad; "[SOIC]" printed in the drawing titles. |
| **`land_*` omitted** | **WRONG** | The single gold defect: the review's "only land pattern is page 29 (8-lead SN)" premise is false — page 33 is the 16-lead SL land pattern (C04-2108A) for the very package the MPN orders. See section 1. |

---

## TALLY

Contested: 3 × RUN (land_pad_length, land_pad_width, land_span), 1 × BOTH (supply-pin grouping). Audit: 16 pins + 10
dimensions + 6 exclusion/provenance items = 32 GOLD, 0 wrong besides the land omission already counted.

TALLY: GOLD 32 · RUN 3 · BOTH 1 · NEITHER 0

GOLD CORRECTIONS:
- `package.dimensions`: add `"land_pad_length": {"max": 1.5, "source": {"page": 33, "quote": "MCP3004/3008"}, "status": "inferred"}`
- `package.dimensions`: add `"land_pad_width": {"max": 0.6, "source": {"page": 33, "quote": "MCP3004/3008"}, "status": "inferred"}`
- `package.dimensions`: add `"land_span": {"nom": 5.4, "source": {"page": 33, "quote": "MCP3004/3008"}, "status": "inferred"}`

(Any gold change must then follow the Gold Modification Arbitration Protocol: record in `evals/cases/mcp3008_soic16/review.md`
that page 33 — "16-Lead Plastic Small Outline (SL) – Narrow, 3.90 mm Body [SOIC]", drawing C04-2108A — is the 16-lead land
pattern, that C = 5.40 NOM is the centre-to-centre pad-row span (C = G + Y = 3.90 + 1.50), X = 0.60 MAX and Y = 1.50 MAX, all
read from the render because the page-33 table has no text layer; rerun `python evals/score.py --extracted …`; commit as
`[GOLD]`. Note the quotes are page-pinning only — the hand-over must say the values need human confirmation against the
render. After the correction, the gold's `build` produces the footprint, which removes the `footprint.skipped` outcome the
review currently describes as correct.)

---

# Adjudication — `sn74hc00_soic14` (round 6)

Adjudicator: independent gold audit. Both extraction runs were scored `usable`, 12/12 dimensions and
14/14 pins, so there is no scored disagreement to settle; per the brief this audit checks **every** gold
pin and dimension against the datasheet, hunting for gold errors that are invisible to the scorer because
both runs agree with the gold.

**Materials.** Rules: `/tmp/round6/skill/SKILL.md`, `/tmp/round6/skill/reference.md`, `example.json`.
Gold: `evals/cases/sn74hc00_soic14/spec.gold.json` + `review.md`. Runs: `evals/runs/round6/sn74hc00_soic14_run1.json`,
`..._run2.json`. Datasheet: `~/datasheets/sn74hc00_soic14.pdf` (TI SCLS181H, 39 pages).

**Method.** `sha256sum` verified (`e53f9214…a4c75`, matches the gold). Every contested item was judged on a
rendered image: pages 23/24 rendered at 300 dpi and 600 dpi (`pdftoppm -r 600`), page 3 at 200 dpi, page 1 and
the addendum (pages 16–19) read as text. Extension lines were traced by pixel measurement (dark-pixel row/column
runs in PIL), anchored to `pdftotext -bbox` word boxes scaled by 600/72. All 26 gold quotes were re-checked
mechanically for contiguous occurrence in whitespace-normalised `pdftotext -layout` page text, and every recorded
value was checked to appear among its own quote's numbers.

**Drawing scale calibration (used throughout).** Top view: lead-tip extension lines at x = 1188 / 2322 (600 dpi);
pitch arrows span 241 px between adjacent lead centrelines; 2X 7.62 extension rows 1440 px apart over 6 intervals
→ 189.7 px/mm. At that scale the drawn geometry sits at each callout's mid-value: tip-to-tip 1138 px = 6.00 mm
(mid of 5.8–6.2), body 737 px = 3.89 mm (mid of 3.8–4.0), body length 1635 px = 8.62 mm (mid of 8.55–8.75),
lead width 77 px = 0.41 mm (mid of 0.31–0.51). DETAIL A: 285 px/mm (lead length drawn 238 px = 0.835 = mid of
0.40–1.27); at that scale the standoff pair measures 58 px = 0.20 (inside 0.10–0.25) and the lead thickness
53 px = 0.186 (inside 0.13–0.25). End view: 194 px/mm (thickness 36 px = 0.186; body 740 px ≈ 3.9 mm). The
drawn geometry is internally consistent with exactly the readings the gold records.

---

## 1. Header block

| Item | Gold | Verdict | Evidence |
|---|---|---|---|
| `mpn` | `SN74HC00D` | **GOLD** | Page 1 Device Information prints `SN74HC00D` for "SOIC (14), 8.70 mm × 3.90 mm". Addendum p. 17 (dated 18-Sep-2026) lists for SOIC (D) \| 14: `SN74HC00D` **Obsolete**, `SN74HC00DR` **Active** (2500 \| LARGE T&R), `SN74HC00DT` Obsolete. reference.md: the mpn is the addendum orderable "suffix and all", but "drop a tape-and-reel or temperature suffix only when the page prints the shorter number". `R` is the tape-and-reel suffix and page 1 prints the shorter number, so `SN74HC00D` is exactly what the rule yields. The Obsolete/Active split changes which orderable is current, not the extraction; the gold's review documents it. |
| `manufacturer` | `Texas Instruments` | **GOLD** | As printed (p. 1, p. 23 footer). |
| `datasheet.sha256` | `e53f9214…` | **GOLD** | Recomputed, matches. |
| `datasheet.revision` | `SCLS181H – DECEMBER 1982 – REVISED AUGUST 2021` | **GOLD** | Verbatim page-1 header string. (Run1's `SCLS181H` and run2's paraphrase are weaker; no value error.) |
| `datasheet.url` | `https://www.ti.com/lit/ds/symlink/sn74hc00.pdf` | note, not scored | Optional field per reference.md; not printed on any page (page 3 prints only the product-folder link names). Not evidence-bearing; no correction. |

## 2. Package block

| Item | Gold | Verdict | Evidence |
|---|---|---|---|
| `family` | `SOIC` | **GOLD** | p. 23: "SOIC – 1.75 mm max height, SMALL OUTLINE INTEGRATED CIRCUIT", drawing `D0014A`. |
| `pin_count` | `14` | **GOLD** | 14 leads in the outline and land pattern; addendum "SOIC (D) \| 14". |
| `exposed_pad` | `false` | **GOLD** | No exposed pad on `D0014A`; the FK/LCCC (p. 3 right) is a sibling package and was correctly ignored. |

## 3. Dimensions — outline, page 23

| Item | Gold | Verdict | Evidence |
|---|---|---|---|
| `pitch` 1.27, `nom`, extracted, p23 `12X 1.27` | | **GOLD** | Rendered: `1.27` is boxed; the dimension line's arrows (x≈2530) span exactly 241 px = 1.27 mm between the centrelines of pins 14 and 13 (189.7 px/mm) — neighbouring leads, the `pitch` span. The boxed-basic question is settled under §3a below. Both runs' values agree; run1's `inferred` status is a defensible caution, not a gold error. |
| `body_length` 8.55–8.75 | | **GOLD** | Extension lines at y = 1504 / 3139 land on the moulded body's top/bottom ends (along the rows); drawn 8.62 = mid. Quote `8.75 2X 8.55 7.62 NOTE 3` contiguous; carries the boxed `2X 7.62` tokens, which the gold does not record. Page 1's "8.70 mm" is the Device Information *nominal* — inside [8.55, 8.75] and the rounding of the 8.65 mid; no contradiction, and reference.md's stacked-pair rule yields min/max exactly as recorded. |
| `body_width` 3.8–4.0 | | **GOLD** | Extension lines at x = 1387 / 2124 land on the body's left/right edges (across); drawn 3.89 = mid. NOTE 4 (interlead flash) is a tolerance note, correctly not folded into the values. |
| `overall_width` 5.8–6.2 | | **GOLD** | Extension lines at x = 1188 / 2322 land on the **lead tips** of pins 1/14 (tips at 1186/2324, normal drafting gap); drawn 6.00 = mid → tip-to-tip across the rows = `overall_width`, not a body dimension. The `TYP` over the top value is the sheet's own oddity; the stacked-pair reading (min/max) matches JEDEC MS-012AB's E1 5.80–6.20 MIN/MAX and is the reading reference.md's value rules produce. |
| `height` 1.75, `max` | | **GOLD** | `1.75 MAX` beside the side view (SEATING PLANE / C datum); matches "SOIC – 1.75 mm max height" in both page headers. |
| `lead_width` 0.31–0.51 | | **GOLD** | `14X` callout on one lead (pin 8's); drawn width 77 px = 0.41 mm, mid of 0.31–0.51. |
| `standoff` 0.10–0.25, inferred | | **GOLD** | The decisive pair, settled at 600 dpi: the `0.25 / 0.10` label (x 4423–4551, y 4610–4742) drives two arrows at x ≈ 4332 whose tips terminate on (upper) the line y = 4490 — the **body underside** (solid line x 3890–4176 under the body mass, extended right as 4211–4361) — and (lower) the line y = 4548 — the **seating plane**, on which the foot rests (foot bottom right end meets it at x ≈ 3700; foot-tip bottom y 4551, level within 3 px). Body underside → seating plane is reference.md's `standoff` definition verbatim. The nearby boxed `[0.25] GAGE PLANE` (dash-dot at y 4472, ≈0.25 above the seating plane) was correctly **excluded** as a datum, not a standoff. `inferred` is the honest status: the anchor decision required pixel tracing. |
| `lead_length` 0.40–1.27, extracted | | **GOLD** | The horizontal callout's left extension drops from the foot **tip** (tip edge x = 3537, extension line x 3537–3538, y 4578–4742); right extension at x = 3775, rising to just below the point where the flat underside's knee turns up into the bend (bottom-surface knee x ≈ 3755–3770) — the tip → start-of-bend span reference.md defines as `lead_length` (not the tip-to-body-face length, which would anchor at the body face x ≈ 3805 and which reference.md excludes). Drawn 238 px = 0.835 = mid of 0.40–1.27 at the DETAIL A scale that also puts the standoff (0.20) and thickness (0.186) inside their printed ranges. Note: review.md's remembered pixel "x≈765" is rough (measured 3775 in page coords); the attribution itself is correct. |
| `lead_thickness` 0.13–0.25, extracted | | **GOLD** | The end-view callout `0.25 TYP / 0.13` (label x 2528–2838, y 4036–4168): its two arrows converge on two short slightly-sloped extension lines (y ≈ 3921 and 3957 at the tip) that continue the lead's **own top and bottom surfaces** (surfaces at y 3918–3925 / 3954–3961) — the arrows straddle the lead material, so the span is thickness, not a gap. Cross-checks: DETAIL A draws the same thickness at 53 px = 0.186 mm; end-view scale 194 px/mm puts the body at ≈3.9 mm. Stacked pair → min 0.13 / max 0.25 per reference.md's value rules; the `TYP`-supplies-`nom` clause covers the single-value case and recording both printed limits is the complete reading. The sheet-vs-JEDEC tension (drawing stricter than MS-012AB's c) is documented in the review; the drawing governs. |
| `land_pad_length` 1.55, p24 `14X (1.55)` | | **GOLD** | Rendered: arrows span pad 1's left/right edges (1960 / 2256; 296 px = 1.55 mm at 191 px/mm) — the pad's long axis, which is the row-to-row / lead-foot direction = "along the lead direction". Parenthesised values are explicitly permitted for `land_*` by reference.md. |
| `land_pad_width` 0.6, p24 `14X (0.6)` | | **GOLD** | Vertical arrow spans pad 1's top/bottom edges (1354 / 1467; 113 px = 0.59 mm). |
| `land_span` 5.4, p24 `(5.4)` | | **GOLD** | The dimension line at the bottom runs between the two vertical dash-dot **column centrelines** — through pad 7's centre (x 2105) and pad 8's centre (x 3128) — centre-to-centre, 1023 px ≈ 5.36 mm ≈ 5.4 (4.25 × the 1.27 pitch, as drawn). Matches reference.md's `land_span` definition. Recorded as one set with the two pad sizes, as required. |

### 3a. The `pitch` boxed-basic tension — ruled defensible

The outline prints pitch only as the boxed basic `12X 1.27` (box confirmed: rectangle x 2754–2932 / y 1445–1524
around the `1.27` text); the land pattern repeats it parenthesised as `12X (1.27)`. reference.md's boxed-basic
sentence — "a reference plane or a datum, not a size: never record it as `standoff`, `lead_length`,
`lead_thickness` or anything else" — read alone would exclude it. But reference.md as a whole does not: the
value-mapping rules list `BSC` among the qualifiers that "get `nom`"; the letter table maps `e` → `pitch`;
and the skill's own `example.json` records `"e 0.95 BSC"` as an **extracted `nom`** pitch. The boxed-basic
prohibition's own two illustrations (a boxed gage-plane offset that would masquerade as a standoff; a
parenthesised lead thickness) target datum/reference material misattributed into size names — the pitch is
not a datum, and its attribution here is unambiguous (arrows between adjacent lead centrelines, verified
241 px = 1.27 mm). The gold took the value from page 23's boxed basic (correct: the parenthesised land-pattern
value "may be used for a `land_*` value and must not become a package dimension", and pitch is not a `land_*`
value), and the review documents the tension instead of resolving it silently. **The record stands.**

## 4. Deliberate exclusions — all correct

| Excluded | Verdict | Why the exclusion is right |
|---|---|---|
| `2X 7.62` (boxed; box y 2288–2370 confirmed) | **GOLD** | Extension dash-dots at y 1602 / 3042 = pin 14 / pin 8 centrelines, 1440 px = 6 × 1.27: a lead centre-to-centre span, which reference.md's `overall_width` clause declines to record — and it is boxed basic besides. |
| Boxed `[0.25] GAGE PLANE` (DETAIL A) | **GOLD** | Gage-plane datum offset (dash-dot 0.25 above the seating plane); reference.md's named example of what must not become a standoff. The standoff came from the `0.25/0.10` arrow callout instead. |
| `0° –8°` | **GOLD** | Lead bend angle; no name in the dimension vocabulary. |
| `⌖ Ø0.25 Ⓜ C A B` | **GOLD** | GD&T position feature control frame, not a size. |
| `0.1 C` (side view) | **GOLD** | Profile tolerance to datum C. |
| `(R0.05) TYP` (p. 24) | **GOLD** | Pad corner radius; no dimension name. |
| `0.07 MAX / 0.07 MIN ALL AROUND` (p. 24) | **GOLD** | Solder-mask openings in the SOLDER MASK DETAILS figures — mask, not metal; the metal pad callouts are present, so nothing was substituted. |
| Notes 3/4 flash allowances; pin-1 ID area | **GOLD** | Tolerance-note values, not callouts; the ID area prints no dimension. |

Also correctly **absent**: `body_thickness` (no separate callout on this sheet), `overall_length` (no
tip-to-tip-along-rows callout exists — the 8.75/8.55 is the body), `land_ep_size` (no exposed pad). Nothing the
sheet gives was skipped; nothing recorded exceeds it.

## 5. Pins — all 14

Each pin was checked three ways: Table 5-1 row (page 3), the rendered top view (page 3, cropped and inspected:
left column 1A–GND = 1–7 top-to-bottom, right column VCC–3Y = 14–8 top-to-bottom), and page 1's functional
pinout. The D column of Table 5-1 gives every pairing the gold records; the FK/LCCC column (and the NC row,
which has no D entry) was correctly ignored as a sibling package's pinout, and no `alt_names` were invented
from it.

| Pin | Gold | Verdict | Pin | Gold | Verdict |
|---|---|---|---|---|---|
| 1 `1A` input | | **GOLD** | 8 `3Y` output | | **GOLD** |
| 2 `1B` input | | **GOLD** | 9 `3A` input | | **GOLD** |
| 3 `1Y` output | | **GOLD** | 10 `3B` input | | **GOLD** |
| 4 `2A` input | | **GOLD** | 11 `4Y` output | | **GOLD** |
| 5 `2B` input | | **GOLD** | 12 `4A` input | | **GOLD** |
| 6 `2Y` output | | **GOLD** | 13 `4B` input | | **GOLD** |
| 7 `GND` power_in, inferred | | **GOLD** | 14 `VCC` power_in, inferred | | **GOLD** |

Types: `input`/`output` straight from the I/O column; `power_in` + `inferred` for GND/VCC through the supply
rule. Three-state check re-run: the sheet's only high-impedance text concerns inputs (§8.4); there is no OE pin
and no output-Z state, so the four Y pins correctly stay `output` (the 74HC595 counter-example does not apply).

## 6. Groups

**GOLD.** The datasheet's own unit key is "Channel 1"…"Channel 4" (Table 5-1 DESCRIPTION column), so the gold's
group keys `1`–`4` follow reference.md's "the key is whatever the datasheet calls the unit … its channel
numbers". Every pin of every unit is grouped. GND/VCC carry `"power"`: the table prints `—` (no `PWR` block),
so this is the reference's optional case — grouping a bare VDD/VSS pair `"power"` and leaving it off are
"equally correct", and the gold's choice is permitted (descriptions "Ground" / "Positive Supply", common to all
four channels). Both runs made the same choice; there is no disagreement to rule on.

## 7. Statuses

**GOLD.** Signal pins `extracted` (number, name and type all read from the table/pinout); supplies `inferred`
(chosen through the supply rule); `standoff` `inferred` (the one dimension whose anchor needed pixel
interpretation); `pitch`, `lead_length`, `lead_thickness` `extracted` (attribution directly readable from the
rendered callouts; disambiguating a lead callout by re-rendering is reference.md's prescribed reading
procedure, not an interpretation that forces `inferred` — run1's more cautious `inferred` on pitch is equally
permitted, and is not a gold error). No `confirmed` anywhere. Correct.

## 8. Quotes

**GOLD.** All 26 gold quotes (12 dimensions + 14 pins) were re-verified as contiguous substrings of the
whitespace-normalised `pdftotext -layout` text of their cited pages (same checker basis as `check_quotes`),
and every recorded value appears among its own quote's numbers. The documented interlopers are real and
harmless: `body_width`'s quote carries `0.31`/`1.75` (recorded under `lead_width`/`height` from their own
quotes), `standoff`'s carries `0 -8`/`1.27`, `lead_length`'s carries `0.10`, `body_length`'s carries the boxed
`7.62` — none is recorded under the dimension the quote anchors. Both runs' quotes also verify contiguous.

---

## Verdict summary

Every audited area of the gold — mpn (including the Obsolete/Active and tape-and-reel-suffix question),
package block, all 12 dimensions (including the three contested attributions, each re-settled by pixel
measurement at 600 dpi), all eight deliberate exclusions, all 14 pins, groups, statuses, and all 26 quotes —
matches the datasheet and reference.md. The two questions flagged in the brief resolve as follows: the boxed
`12X 1.27` pitch is recordable under reference.md read as a whole (BSC rule, letter table, `example.json`
precedent), and the `0.25 TYP/0.13` ↔ `0.25/0.10` attribution is confirmed by extension-line tracing (end-view
arrows straddle the lead material = thickness; DETAIL A right callout spans body underside → seating plane =
standoff), with the drawn geometry internally consistent at one scale per view. The gold's review.md honestly
documents both tensions and the `6.2 TYP` oddity. No gold error was found that either run got right; the only
cross-run deltas are status/quote-stretch choices the rules permit.

TALLY: GOLD 44 · RUN 0 · BOTH 0 · NEITHER 0

(item count: 4 header + 3 package + 12 dimensions + 8 exclusions + 14 pins + groups + statuses + quotes)

GOLD CORRECTIONS: none

---

# Adjudication — `pcf8574_soic16` (extraction round 6)

**Materials.** Rules: `/tmp/round6/skill/SKILL.md`, `/tmp/round6/skill/reference.md`. Gold:
`evals/cases/pcf8574_soic16/spec.gold.json` + `review.md`. Runs: `evals/runs/round6/pcf8574_soic16_run1.json`,
`..._run2.json`. Datasheet: `~/datasheets/pcf8574_soic16.pdf` (TI SCPS068K, 39 pages).

**Method (all verification new for this report).** `sha256sum` recomputed =
`9f2c7693d36498aaa8f8962589c6062d3c093136ace85090d935aff3967a8079` — matches the gold (the runs record the same
hash). `kicad-partspec validate --datasheet` re-run on all three files: **0 failed findings each**; all 28 quotes
per run mechanically found on their cited pages; the gold carries exactly the 4 deliberate `inferred` advisories
(pins GND/INT/VCC + dimension standoff), the runs 3 each. All three specs built with `kicad-partspec build` into
scratch dirs (`/tmp/round6/pcfbuild/`): 0 failures. Renders: page 3 at 200 dpi (Figure 4-4), page 36 at 150 dpi
(whole DW0016A sheet) and 600 dpi with pixel measurement of every contested callout, page 37 at 300 dpi (land
pattern). Text-token positions anchored with `pdftotext -bbox` scaled by 600/72. Scale calibrations used below:
top view **141.7 px/mm** (pitch arrows 180 px = 1.27 mm); DETAIL A **248 px/mm** (boxed gage-plane offset 62 px =
0.25 mm exact); land pattern SCALE 7X (11.81 px/mm at 300 dpi, drawn 7× life).

**Scorer frame.** Both runs: 16/16 pins found, names/types/alts 16/16, dims 12/12, quotes 28/28, statuses 16/16;
`groups_ok` 8/16; `symbol_identical: false`; `usable_without_edit: false`. The **only** field-level disagreement
is `group` on pins 4–7 and 9–12.

---

## 1. Contested item — the `group` field on pins 4–7 and 9–12 (P0–P7)

| Source | Record |
|---|---|
| gold | pins 4–7, 9–12 carry `"group": "P0"` … `"P7"` (each Pn pin its own key); all other pins ungrouped |
| run1, run2 | all 16 pins ungrouped ("P0–P7 are one quasi-bidirectional port, not repeated multi-pin units") |

**Verdict: RUN** (the runs are right; the gold's per-pin groups must be removed).

**Evidence.**

1. *The datasheet's own vocabulary never individuates the P-pins into units.* It prints, on page 1
   (§3 Description): "The device features an **8-bit quasi-bidirectional I/O port (P0–P7)**" and "Each
   quasi-bidirectional I/O can be used as an input or output without the use of a data-direction control signal."
   Table 4-1 (page 3) collapses all eight into **one row** — NAME `P[0..7]`, one TYPE cell `I/O`, DESCRIPTION
   "P-port input/output. Push-pull design structure." §7.2/Figure 7-2 (page 12) is titled "Simplified Schematic
   Diagram of **Each P-Port Input or Output**". The word "channel" does not occur anywhere in the datasheet
   (whole-document grep: zero hits). The unit the datasheet names and shows is **the port** — one block whose
   eight bits are P0–P7 — exactly the "bits of one port" reading the runs took.

2. *reference.md's unit examples are all datasheet-named channel/unit structures, and its own port clause makes
   a port a block, not a unit.* The bullet requires grouping "whenever the datasheet shows repeated, identical
   functional blocks — two identical amplifiers, a quad gate, N numbered channels", with the key "whatever the
   datasheet calls the unit — its letters "A", "B", its channel numbers "1"–"7", its channel names "CH0"–"CH7"".
   The exclusion sentence then rules: "the A port and B port of a level translator, the two banks of a memory, or
   **an input port and its matching output port stay ungrouped**" — establishing that a **port is a block, not a
   unit**. The PCF8574 has one such block (the P-port); there are no two sides to confuse, and no channel
   language to key from. The gold review's justification — "the reference's 'channel names CH0–CH7' pattern" —
   imports a vocabulary the datasheet does not use.

3. *The corpus's settled reading of the same prose on structurally identical pins is ungrouped.*
   - `evals/cases/74hc595_so16`: Q0–Q7, eight identical outputs of one register, individually rowed in the NXP
     pin table — **ungrouped** in the accepted gold.
   - `evals/cases/mcp23008_soic18`: GP0–GP7, eight bidirectional I/O pins of one port on an I²C expander — the
     PCF8574's nearest sibling architecture — each with its **own** table row ("GP0 … I/O Bidirectional I/O pin…",
     Table 1-1) — **ungrouped** in the accepted gold.
   - `evals/cases/txs0108e_tssop20`: A1–A8/B1–B8 — **ungrouped**, and this case is named by reference.md itself.
   - The corpus golds that DO group per-pin keys do so because the datasheet says *channel*: MCP3008 (CH0–CH7,
     "8-Channel" mux; the round-6 mcp3008 adjudication held that grouping "required by the prose"), TCA9548A
     (CH0–CH7, each a two-pin SDn+SCn unit), ULN2003A (channels 1–7), LM393B (comparators 1/2). If the PCF8574
     gold's reading were adopted, the 74hc595 and mcp23008 golds would have to be wrong by the same reasoning —
     the corpus would be self-contradictory. Reading the prose consistently with the corpus, the P-port bits stay
     ungrouped.

4. *Render check of the pairing itself (independent of the group question):* Figure 4-4 rendered at 200 dpi
   confirms all 16 number↔name pairs exactly as both files record them (left column A0=1, A1=2, A2=3, P0=4,
   P1=5, P2=6, P3=7, GND=8; right column VCC=16, SDA=15, SCL=14, INT=13, P7=12, P6=11, P5=10, P4=9). The
   caption's "20 Pins" typo is confirmed (16 pins in the figure; §5.4 thermal table "DW … 16 PINS"; addendum
   "SOIC (DW) | 16") — the review already documents it.

**Correction to apply:** remove the eight `group` fields from the gold (exact JSON paths under GOLD CORRECTIONS).
After the correction the runs agree with the gold on every field.

---

## 2. Contested item — the generated-symbol difference (both runs flagged)

All three specs were built and the outputs diffed. run1 and run2 generate **byte-identical** symbols and
byte-identical footprints; the footprints of all three files are **byte-identical** (same 12 dimensions). The
gold's symbol differs from the runs' in exactly two independent causes:

1. **Unit structure — caused by the `group` field alone (contested item 1).** `gen/symbol.py` makes one unit per
   named group plus one unit for ungrouped pins. Gold: **9 units** — units 1–8 = P0…P7 (one single-pin unit each,
   rectangle ±2.54, pin at −7.62,0), unit 9 = the eight ungrouped pins (A0, A1, A2, SCL, INT, SDA, VCC, GND),
   root Reference property at (0, 16.51). Runs: **1 unit** holding all 16 pins (rectangle ±15.24, pins stacked at
   ±7.62), root Reference property at (0, 20.32). Every unit rectangle, every pin coordinate and the root `at`
   differ as a consequence. With the RUN verdict this structure is the runs' correct outcome, not a defect of
   theirs; the gold's 9-unit symbol is what must change.
2. **`Datasheet` property — caused by `datasheet.url`, independent of the groups and present in both runs.** The
   gold records `"url": "https://www.ti.com/lit/ds/symlink/pcf8574.pdf"` and the generated symbol carries it;
   the runs omit the field, so the property is `""`. reference.md marks `url` **optional**, and the URL is the TI
   product-folder symlink form, not a string printed on any page — so either record is compliant. This is
   provenance metadata, not a pin or dimension error, and it would survive fixing the groups.
3. **No other cause exists**: the full diff shows no property-ordering, naming, type or geometry differences
   beyond the two above (verified on the byte-level diff of all three builds).

Note on the scorer: `symbol_identical` is a field proxy, not a file diff — it fails when `groups_ok < 16`. After
the gold correction both runs pass the proxy; the residual file-level `Datasheet`-property difference is the
optional-field choice above and is not scored.

---

## 3. Independent gold audit — every pin

All 16 pairings verified on the rendered Figure 4-4 (page 3, 200 dpi) and against Table 4-1 (page 3). Quotes
mechanically re-verified (28/28 found; each recorded value appears among its own quote's tokens). The RGT/RGY and
DGV/PW columns and figures of page 3 are sibling-package pinouts and are correctly absent from names and
`alt_names` (no `alt_names` anywhere — correct: Table 4-1 prints one symbol per pin, and `INT` is printed plain,
KiCad's `~{INT}` being notation, not a second name).

| Pin | Gold record | Verdict | Evidence |
|---|---|---|---|
| 1 | A0, input, extracted, p3 `A0 1 16 VCC` | **GOLD** | Fig 4-4 render + Table 4-1 `A [0..2] … 1, 2, 3 I` ("Address inputs 0 through 2"). |
| 2 | A1, input, extracted, p3 `A1 2 15 SDA` | **GOLD** | Same row/figure. |
| 3 | A2, input, extracted, p3 `A2 3 14 SCL` | **GOLD** | Same row/figure. |
| 4 | P0, bidirectional, extracted, p3 `4 13 INT P0` | **GOLD** (except `group` — item 1, RUN) | Fig 4-4: P0 sits one text row below pin 4's number (rotated label), which is why the quote spans the rows; type from the `P[0..7]` row's `I/O`. |
| 5 | P1, bidirectional, extracted, p3 `P1 5 12 P7` | **GOLD** (except `group`) | Fig 4-4 + table row. |
| 6 | P2, bidirectional, extracted, p3 `P2 6 11 P6` | **GOLD** (except `group`) | Fig 4-4 + table row. |
| 7 | P3, bidirectional, extracted, p3 `P3 7 10 P5` | **GOLD** (except `group`) | Fig 4-4 + table row. |
| 8 | GND, power_in, inferred, p3 `GND 8 9 P4` | **GOLD** | Table 4-1 prints `—` in TYPE, description "Ground"; ground → `power_in` with status `inferred` per the reference type table. |
| 9 | P4, bidirectional, extracted, p3 `GND 8 9 P4` | **GOLD** (except `group`) | Fig 4-4 + table row. |
| 10 | P5, bidirectional, extracted, p3 `P3 7 10 P5` | **GOLD** (except `group`) | Fig 4-4 + table row. |
| 11 | P6, bidirectional, extracted, p3 `P2 6 11 P6` | **GOLD** (except `group`) | Fig 4-4 + table row. |
| 12 | P7, bidirectional, extracted, p3 `P1 5 12 P7` | **GOLD** (except `group`) | Fig 4-4 + table row. |
| 13 | INT, open_collector, inferred, p3 `4 13 INT` | **GOLD** | Table 4-1: `O — "Interrupt output. Connect to VCC through a pullup resistor."`; page 1 feature list: "Open-drain interrupt output" → the open-drain row of the type table, status `inferred`. The type evidence is on page 1 while the quote stays on the pin's own page 3 — per the gold review, and legitimate. |
| 14 | SCL, input, extracted, p3 `A2 3 14 SCL` | **GOLD** | Table row `I "Serial clock line…"`. |
| 15 | SDA, bidirectional, extracted, p3 `A1 2 15 SDA` | **GOLD** | Table row `I/O "Serial data line…"`. |
| 16 | VCC, power_in, inferred, p3 `A0 1 16 VCC` | **GOLD** | Table 4-1 prints `—`, description "Voltage supply" → supply row, `inferred`. |

**Group scheme for the non-P pins — GOLD.** A0–A2 are address pins ("Pins with no unit of their own — an address
pin … stay ungrouped"); SCL/SDA/INT have no unit. GND/VCC: Table 4-1's TYPE column prints `—` (no `PWR` block),
so this is the reference's explicitly optional case — "grouping it `"power"` is optional and leaving `group` off
it is equally correct". The gold leaves them off; both runs agree.

**Statuses — GOLD.** Signal pins `extracted` (number/name verified on the render, type from the TYPE column);
GND/INT/VCC `inferred` through the supply/open-drain rows. `extracted` on the P-pins is earned. No `confirmed`
anywhere.

---

## 4. Independent gold audit — every dimension

All 12 verified on the 600-dpi render of page 36 (DW0016A) and the 300-dpi render of page 37, with pixel
measurement. The drawn geometry is internally consistent at one scale per view with exactly the readings the gold
records (top view 141.7 px/mm: tip-to-tip 1465 px = 10.34, body 1063 px = 7.50, body ends 1460 px = 10.30, pitch
180 px = 1.27, lead width 58 px = 0.41, `2X 8.89` = 1260 px = 8.89 exact; DETAIL A 248 px/mm).

| # | Name (gold) | Verdict | Evidence |
|---|---|---|---|
| 5 | `pitch` nom 1.27, extracted, p36 `14X 1.27` | **GOLD** | Box confirmed (box edges x 3008–3186, y 1450–1546 around `1.27`, `14X` outside); arrows between pin 16/15 centrelines (dash-dot rows y 1620/1800 = 180 px = 1.27 mm). The boxed-basic tension is settled as in the sn74hc00 round-6 adjudication §3a: reference.md read whole (BSC→`nom`, letter table `e`→pitch, example.json's `"e 0.95 BSC"`) records the pitch; the boxed-basic prohibition targets gage-plane/datum offsets. |
| 6 | `body_length` 10.1–10.5, extracted, p36 `10.5 2X 10.1 8.89 NOTE 3` | **GOLD** | Extension lines land on the moulded body's two ends (y 1520/2980; drawn 1460 px = 10.30 = mid of 10.1–10.5). Leads exit the two long sides only, so no tip-to-tip-along-rows callout exists → `overall_length` rightly absent rather than a renamed body dim. Page 1's Package Information "SOIC (DW, 16) 10.3mm × 10.3mm" is a nominal *including pins* (note 2 on page 1) — 10.3 is the body-length nominal and simultaneously the tip-span nominal; the review's reading is confirmed by the drawn 10.30/10.34, no contradiction. Stacked pair → min/max per the value rules. |
| 7 | `body_width` 7.4–7.6, extracted, p36 `7.6 B 0.25 C A B 2.65 MAX 7.4 NOTE 4` | **GOLD** | Extension lines at x 1315/2378 = the body's left/right edges (across the rows; drawn 1063 px = 7.50 = mid). Quote carries the page's own token stretch; NOTE 4 is the interlead-flash tolerance, not folded into values — correct. |
| 8 | `overall_width` 9.97–10.63, extracted, p36 `10.63 SEATING PLANE TYP 9.97` | **GOLD** | The decisive check: the callout's two extension lines land at x 1114/2579 — the **lead tips** of pins 1 and 16 (body edges at 1315/2378 are 201 px = 1.42 mm inside each) — tip-to-tip across the rows, the reference's `overall_width`. Drawn 1465 px = 10.34 ≈ the mid of 9.97–10.63. The `TYP` sits over the stacked pair; two printed values → min/max (the same ruling as the `5.8–6.2 TYP` on the sibling D0014A sheet); the `SEATING PLANE` tokens in the quote are the interleaved end-view label of the same text-layer stretch — on-page, and the values are read from the right callout. |
| 9 | `height` max 2.65, extracted, p36 `2.65 MAX` | **GOLD** | End view: arrows span the body top to the dash-dot SEATING PLANE (datum C); both page headers print "SOIC - 2.65 mm max height". MAX → max only. |
| 10 | `lead_width` 0.31–0.51, extracted, p36 `0.51 16X 0.31` | **GOLD** | `16X` callout straddling one lead in the top view; drawn 58 px = 0.41 = mid of 0.31–0.51; 16 leads. |
| 11 | `lead_thickness` 0.10–0.33, extracted, p36 `0.33 TYP 0.10` | **GOLD** | The twin-callout trap, settled by extension lines at 600 dpi: the side-view callout's two arrows converge on the two thin parallel lines (y 3840/3875) that **continue the foot's own top and bottom surfaces** past the toe — the arrows straddle the lead material → "the two edges of one lead's cross-section, in the front or side view" = `lead_thickness` (drawn gap 35 px ≈ 0.25 at the top-view scale, inside 0.10–0.33). DETAIL A's near-twin `0.3/0.1` is a different callout (next row). Swapping the two — as the review warns — would give standoff 0.10–0.33/thickness 0.10–0.30; the gold did not swap. |
| 12 | `standoff` 0.10–0.30, **inferred**, p36 `0.3 0 -8 0.1` | **GOLD** | Pixel-traced independently: upper arrow (tip y 4398) touches the thin extension line at y 4398–4400 (x 3977–4165), collinear across a 37 px drafting gap with the thick **body-underside** line (y 4396–4402, x 3707–3940 — the lowest edge of the body mass in DETAIL A); lower arrow (tip y 4469) touches the long **seating-plane** line (y 4469–4471, x 3433–4165). Span drawn 71 px = 0.29 mm ≈ 0.30 (max condition). The dotted **gage plane** (y 4404–4412, the boxed `0.25`'s target — box confirmed at x 2877–3055/y 4149–4245) sits 9 px *below* the body-underside line, i.e. the detail is drawn near max standoff where 0.30 > 0.25 — matching the review's forensic account. Body underside → seating plane is reference.md's `standoff` row verbatim. `inferred` is the honest status: three candidate upper anchors (body underside y 4399, dotted gage plane y 4408, sloped foot top y 4392–4398) lie within ~0.04 mm of each other and the attribution needed pixel tracing. |
| 13 | `lead_length` 0.40–1.27, extracted, p36 `1.27 0.40` | **GOLD** | DETAIL A's three vertical extension lines measured at x 3320 / 3517 / 3650: x 3320 = the **toe** (leftmost foot material, x 3314); x 3517 = the **start of the bend** (the knee where the flat foot's surfaces curve up); x 3650 = the **body face** (the slanted body-left-face line meets its extension there). The `1.27/0.40` arrows span 3320→3517 = tip → bend start, drawn 197 px = 0.79 ≈ the mid of 0.40–1.27 (0.835) — the reference's `lead_length`. `(1.4)` spans 3320→3650 = toe → body face: parenthesised AND the body-face-to-tip length the reference explicitly excludes — correctly left out. |
| 14 | `land_pad_length` nom 2.0, extracted, p37 `16X (2)` | **GOLD** | Rendered: arrows span pad 1's long (horizontal) axis — the lead direction, since the pad rows run vertically toward the body — measured 166 px = 2.01 mm at SCALE 7X. Parenthesised values are explicitly permitted for `land_*`. |
| 15 | `land_pad_width` nom 0.6, extracted, p37 `16X (0.6)` | **GOLD** | Vertical arrows span pad 1's short edges; measured 50 px = 0.605 mm. |
| 16 | `land_span` nom 9.3, extracted, p37 `(9.3)` | **GOLD** | The dimension line (y 1565, x 865→1634, 769 px = exactly 9.30 mm at 7X) runs between the two **pad-column centrelines** (left pads centred x 865, right pads x 1634 — dash-dot centre-lines through the columns) → centre-to-centre `land_span` per the reference. Recorded together with the two pad sizes as the reference requires ("together or not at all"). |

**Deliberate exclusions — all GOLD.** Boxed `2X 8.89` (end-lead centre-to-centre span, 7 × 1.27 — a lead
centre-to-centre span is not recorded, and it is boxed basic); boxed `0.25 GAGE PLANE` (gage-plane datum offset —
the reference's named never-a-standoff); `(1.4) TYPICAL` (see `lead_length`); `0.1 C` (profile tolerance to datum
C); datums A/B/C; `⌖ 0.25Ⓜ C A B` (positional FCF); `0°–8°` (bend angle); `R0.05 TYP` (pad radius); page-37
solder-mask `0.07 MAX/MIN` (mask, not the metal pad callouts, which are present); page 38 stencil (not the land
pattern); `body_thickness` (DW0016A prints no A2 row); `land_ep_size` (no exposed pad); `overall_length` (no
tip-to-tip-along-rows callout). Nothing the sheet gives was skipped; nothing recorded exceeds it.

---

## 5. Independent gold audit — metadata and provenance

| Item | Gold | Verdict | Evidence |
|---|---|---|---|
| `mpn` | `PCF8574DW` | **GOLD** | Addendum (page 24) lists for SOIC (DW) \| 16: `PCF8574DW` **Obsolete**, `PCF8574DWR` Active (2000 \| LARGE T&R), plus `.A`/`G4` forms. reference.md: the mpn is an orderable the addendum lists, and a tape-and-reel suffix may be dropped "only when the page prints the shorter number" — the page prints `PCF8574DW` itself as an orderable row, so the shorter form is exactly what the rule yields. The Obsolete/Active split changes which orderable is current, not the extraction; identical situation ruled GOLD in the sn74hc00 round-6 adjudication (`SN74HC00D` Obsolete vs `SN74HC00DR` Active). The A-variant orderables are a different part, correctly untouched. |
| `manufacturer` | Texas Instruments | **GOLD** | Page 1 and page footers. |
| `datasheet.sha256` / `revision` | `9f2c7693…a8079` / `SCPS068K – JULY 2001 – REVISED SEPTEMBER 2024` | **GOLD** | Hash recomputed, identical; revision string verbatim from the page-1 header (en dashes as printed). |
| `datasheet.url` | recorded | note | Optional per reference.md and not printed on any page; harmless either way — but it is the sole cause of the residual symbol `Datasheet`-property difference (section 2.2). |
| `package.family` / `pin_count` / `exposed_pad` | SOIC / 16 / false | **GOLD** | DW0016A header "SOIC - 2.65 mm max height"; 16 leads in outline and land pattern; addendum "SOIC (DW) \| 16"; no exposed pad. |
| Quotes | 28/28 | **GOLD** | All mechanically contiguous in whitespace-normalised `pdftotext -layout` page text (checker basis re-run); each recorded value appears among its own quote's numbers; no quote names a different callout (the interleaved-token stretches `10.63 SEATING PLANE TYP 9.97`, `7.6 B 0.25 C A B 2.65 MAX 7.4 NOTE 4`, `0.3 0 -8 0.1` were each verified against the render to anchor the right callout). |

**Run-quality notes (not scored, no gold change).** Both runs mark `standoff` `extracted` while the gold says
`inferred`; given the three near-coincident candidate anchors (§4 row 12), `inferred` is the honest status and the
runs over-claim — a status choice the checker and scorer do not test. run1's `datasheet.revision` `"SCPS068K"` is
shorter than the page-1 string (run2 carries the full string); run1's A0–A2 quotes are the garbled interleaved
Table 4-1 row (on-page and checker-passing, but run2's Figure 4-4 quotes are the better evidence). Both runs omit
the optional `datasheet.url`.

---

## Verdict summary

The single scored disagreement — the `group` field on P0–P7 — goes to the runs: the datasheet presents P0–P7 as
the bits of one 8-bit quasi-bidirectional I/O port (one table row `P[0..7]`, "P-port input/output", no channel
vocabulary anywhere), and reference.md's own port clause plus the corpus's accepted golds for the identical
structures (74hc595 Q0–Q7, mcp23008 GP0–PG7, txs0108e A/B) leave port bits ungrouped. The generated-symbol
difference decomposes into exactly two causes: the group field (contested item 1) and the optional
`datasheet.url` (provenance only). The independent gold audit found every pin, every dimension, the land set, all
exclusions, the statuses and all 28 quotes correct against the datasheet — the gold's only defect is the eight
group keys. The gold review's two forensic claims (the `10.63 TYP/9.97` tip-to-tip span; DETAIL A's `0.3/0.1` =
body underside → seating plane with the dotted gage plane a step below) were both reconfirmed by pixel
measurement at 600 dpi.

TALLY: GOLD 36 · RUN 1 · BOTH 0 · NEITHER 0

(item count: 2 header/mpn + 1 package block + 12 dimensions + 16 pins + group scheme for non-P pins + statuses +
quotes + exclusions = 36 GOLD; the P-pin group item = RUN)

GOLD CORRECTIONS:
- `pins[3]` (pin 4, P0): remove `"group": "P0"`
- `pins[4]` (pin 5, P1): remove `"group": "P1"`
- `pins[5]` (pin 6, P2): remove `"group": "P2"`
- `pins[6]` (pin 7, P3): remove `"group": "P3"`
- `pins[8]` (pin 9, P4): remove `"group": "P4"`
- `pins[9]` (pin 10, P5): remove `"group": "P5"`
- `pins[10]` (pin 11, P6): remove `"group": "P6"`
- `pins[11]` (pin 12, P7): remove `"group": "P7"`

(Any gold change must follow the Gold Modification Arbitration Protocol: record in
`evals/cases/pcf8574_soic16/review.md` that P0–P7 are the bits of one 8-bit quasi-bidirectional I/O port —
page 1 "8-bit quasi-bidirectional I/O port (P0–P7)", Table 4-1 single row `P[0..7]` / "P-port input/output",
no "channel" vocabulary anywhere in SCPS068K — and that port/register bits stay ungrouped per reference.md's
port clause and the corpus's 74hc595/mcp23008/txs0108e golds; rerun `python evals/score.py --extracted …` to
confirm the correction does not wash scores for existing runs (both round-6 runs then match the gold 16/16 on
groups); commit as `[GOLD]`. After the correction the gold's build yields the runs' 1-unit symbol, and the only
remaining file-level symbol delta is the optional `Datasheet` property.)

---

# Adjudication — `mcp9808_msop8`, extraction round 6

Adjudicator's independent audit. Materials read in full: `/tmp/round6/skill/SKILL.md`,
`/tmp/round6/skill/reference.md`, `evals/cases/mcp9808_msop8/spec.gold.json`,
`evals/cases/mcp9808_msop8/review.md`, `evals/runs/round6/mcp9808_msop8_run1.json`,
`evals/runs/round6/mcp9808_msop8_run2.json`, plus the runs' working directories under
`/tmp/round6/mcp9808_msop8_run{1,2}/`.

Method (all evidence below is first-hand, not taken from the review):

- Datasheet `~/datasheets/mcp9808_msop8.pdf` sha256
  `9578bb72de18d76830ce34f256ef36b400542a3e7bbb9c6d0b74f0a72577ee11` — matches gold and both runs. 52 pages.
- Rendered pages 1 and 38–41 at 200 dpi, page 40 and 41 again at 600 dpi with crops of the
  side view, front view, land-pattern figure and land table; page 1 cover read for the pinout figure.
- Decoded the CID-font text layer of pages 38/40 by shifting every byte +0x1D (`\x13`→`0`,
  `\x11`→`.`, `\x03`→space, `3LWFK`→`Pitch`) with a Python pass over the raw
  `pdftotext -layout` bytes; result matches the printed tables row for row, including the
  drawing codes `C04-123C` (p38) and `C04-111B` (p40). The decode story in the gold's review
  is exactly what the bytes do.
- Ran the repo's own tools read-only: `kicad-partspec validate` on gold, run1, run2 against
  the PDF (quote check), and `kicad-partspec build` on all three into `/tmp`
  (footprint reproduction). No repo file was modified.
- Cross-checked the KiCad library footprint
  `/usr/share/kicad/footprints/Package_SO.pretty/MSOP-8_3x3mm_P0.65mm.kicad_mod`.

Bottom line: **the gold is right and both runs are wrong on the only scored disagreement**
(the MSOP land pattern on page 41). The full independent gold audit found **no gold error**
in any pin, dimension, quote, status or metadata field.

---

## 1. Run 1 (`evals/runs/round6/mcp9808_msop8_run1.json`)

Run1 records 10 outline dimensions (all equal to the gold's) and no `land_*` dimensions; its
build emitted `footprint.skipped` (reproduced: `out/` contains only
`MCP9808-E_MS.kicad_sym`, warning `footprint.skipped: 1`, 0 failures).

### Item 1.1 — `land_span` 4.40 nom (gold) vs absent (run1) — verdict: **GOLD**

- PDF page 41 is titled "8-Lead Plastic Micro Small Outline Package (MS) [MSOP]" (rendered,
  read at 200 and 600 dpi) and prints "RECOMMENDED LAND PATTERN" above an 8+8-pad figure;
  the table is captioned "Microchip Technology Drawing No. C04-2111A".
- Row "Contact Pad Spacing | C" prints a single value **4.40** in the NOM column (600 dpi
  crop read letter by letter). On the figure, C's extension lines land on the two **dashed
  pad-row centre-lines** (Z, further out at 5.85 MAX, spans the pad outer edges), so C is
  centre-to-centre between opposite pad rows — exactly reference.md's `land_span`
  definition. Single NOM value → `nom` per reference.md. Internal consistency: C = Y1 + G1
  = 1.45 + 2.95 = 4.40 and Z = C + Y1 = 4.40 + 1.45 = 5.85, as the review states.
- The three land dimensions are one set per reference.md; the datasheet gives all three, so
  omitting them is a defect, not an honest skip. Run1 is wrong; the gold's 4.40 is what the
  page prints.

### Item 1.2 — `land_pad_length` 1.45 max (gold) vs absent (run1) — verdict: **GOLD**

- Page 41 table row "Contact Pad Length (X8) | Y1" prints **1.45** in the MAX column
  (verified at 600 dpi). On the figure, Y (Y1) spans the vertical extent of one pad
  rectangle — the metal. MAX value → `max` only. Gold correct.

### Item 1.3 — `land_pad_width` 0.45 max (gold) vs absent (run1) — verdict: **GOLD**

- Page 41 table row "Contact Pad Width (X8) | X1" prints **0.45** in the MAX column (600
  dpi). On the figure, X spans one pad's width across. Gold correct.

### Root cause of run1's miss (attribution, not a verdict item)

The claim that the datasheet has no MSOP land pattern is factually wrong. It exists on page
41 — but **text search cannot find it on this datasheet**: pages 38–41 use the CID `Symbol`
font, so the words "RECOMMENDED LAND PATTERN" appear on no extractable line (only the real-ASCII
header note on pages 39/41 and the footers extract; `grep -i "land"` over the full
`pdftotext -layout` dump returns nothing). The skill's step 1 hint ("search for the drawing
code or PACKAGE OUTLINE") therefore fails silently here, and the honest fallback is to read
the drawing pages themselves — the packaging chapter spans PDF pages 37–41 only (verified:
the "most current package drawings" note appears on pages 39/41, and pages 42–52 are
notes/license/appendices). Run1 rendered pages 1, 38 and 40 (see its working dir:
`p01-01.png`, `p38-38.png`, `p40-40.png`) but never rendered pages 39/41, and concluded
"no land pattern" — a wrong negative, not a datasheet fact.

### Unscored run1 differences (attribution)

- `manufacturer`: `"Microchip Technology"` — the sheet prints "Microchip Technology Inc."
  (cover description and every page footer); run1 dropped "Inc.". Flows into the built
  symbol's Description property.
- `datasheet.revision`: `"DS25095A"` is the document number, not a revision; the printed
  revision string is "Revision A (October 2011)" (Appendix B, PDF page 47, printed page 49).
  Cosmetic, unscored.
- `datasheet.url` omitted: reference.md marks the field **optional**, so this is not a
  defect — but it is one of the three reasons the generated symbol file differs from the
  gold's (the build writes the URL into the symbol's `Datasheet` property; run1's is empty).
- Run1's pins and 10 outline dimensions are identical to the gold's (values, pages, types,
  statuses; quotes differ only in whitespace handling, which the quote check ignores).

---

## 2. Run 2 (`evals/runs/round6/mcp9808_msop8_run2.json`)

Run2 is the same extraction as run1 with the full `pdftotext -layout` rows as quotes
(its `quotes_raw.json` shows the same byte-exact garbled rows the gold uses) and the full
manufacturer string. Build reproduced: symbol only, `footprint.skipped: 1`, 0 failures.

### Item 2.1 — `land_span` — verdict: **GOLD** (same evidence as Item 1.1: page 41, drawing C04-2111A, C = 4.40 NOM between the dashed pad-row centre-lines)

### Item 2.2 — `land_pad_length` — verdict: **GOLD** (page 41, Y1 = 1.45 MAX)

### Item 2.3 — `land_pad_width` — verdict: **GOLD** (page 41, X1 = 0.45 MAX)

### Root cause (attribution)

Same as run1: run2 rendered pages 1, 10 and 40 (`p01-01.png`, `p10-10.png`, `p40-40.png`,
`quotes_p40.json`) and never looked at pages 39/41; the text layer offers no searchable land
pattern. Run2 did all the hard parts right (CID decode, byte-exact garbled quotes, correct
outline reading) and lost the footprint purely by not turning one more page.

### Unscored run2 differences (attribution)

- `datasheet.revision`: `"A"` — a short form of the printed "Revision A (October 2011)";
  acceptable, cosmetic.
- `datasheet.url` omitted (optional; leaves the symbol's `Datasheet` property empty).
- `manufacturer` and all pins/dimensions match the gold exactly, so run2's generated symbol
  differs from the gold's in exactly two properties: `Footprint` (empty vs
  `partspec:MSOP-8_3.0x3.0mm_P0.65mm`) and `Datasheet` (empty vs the URL).

---

## 3. Independent gold audit

Every gold field checked against the datasheet; renders at 200/600 dpi, the +0x1D decode,
the repo validator, build reproductions, and the KiCad library were all used first-hand.
Verdict vocabulary per item: whether the **gold** record is correct.

### Item 3.1 — pins 1–8: numbers, names, quotes — verdict: **GOLD**

Table 3-1 (PDF page 11, real text, read directly) prints, MSOP column: 1 SDA Serial Data
Line / 2 SCL Serial Clock Line / 3 Alert Temperature Alert Output / 4 GND Ground / 5 A2
Slave Address / 6 A1 Slave Address / 7 A0 Slave Address / 8 VDD Power Pin; row 9 prints
`—` under MSOP (EP is DFN-only, as the cover note "* Includes Exposed Thermal Pad (EP); see
Table 3-1" confirms on the DFN diagram only). The cover "8-Pin MSOP" figure gives the same
pairing (read at 150 dpi): SDA 1, SCL 2, Alert 3, GND 4, A2 5, A1 6, A0 7, VDD 8. All 8
gold quotes are whitespace-collapsed forms of the page-11 rows; the repo validator
(`quote_not_found` check) and an independent whitespace-normalized scan both find every one
on page 11. One name per physical pin, no EP pin for MSOP: correct.

### Item 3.2 — pin types and statuses — verdict: **GOLD**

- SDA `bidirectional`/`extracted` — §3.1 "SDA is a bidirectional input/output pin" (port
  description ⇒ extracted per reference.md).
- SCL `input`/`extracted` — §3.2 "The SCL is a clock input pin."
- A2/A1/A0 `input`/`extracted` — §3.5 "These pins are device address input pins."
- Alert `open_collector`/`inferred` — §3.3 "the temperature Alert output pin is an
  open-drain output"; reference.md maps "open drain / open collector output" →
  `open_collector` with status `inferred`. Correct, including the status.
- GND `power_in`/`inferred` (§3.4 system ground pin) and VDD `power_in`/`inferred` (§3.6
  power pin) — the supply/ground mapping row, status `inferred`. Correct.

### Item 3.3 — `group` / `alt_names` absence — verdict: **GOLD**

No repeated functional blocks exist on this part, so no group is required; the reference
explicitly keeps address pins ungrouped and calls grouping a lone VDD/GND pair optional.
No pin has a second function (Table 3-1 gives one function per pin; the DFN/MSOP column
pairing in each quoted row is the sibling-package case the reference says to leave in the
hand-over, which the review does). Empty everywhere: correct.

### Items 3.4–3.13 — the ten outline dimensions (all page 40, drawing C04-111B) — verdict: **GOLD** each

Verified three ways: 200 dpi full-page read, 600 dpi crops of the side and front views, and
the +0x1D decode of the text-layer rows. All three agree on every cell.

| # | dim | gold | page prints | letter mapping |
|---|---|---|---|---|
| 3.4 | `pitch` nom 0.65 | Pitch e 0.65 BSC | e → pitch | BSC → nom, per reference |
| 3.5 | `body_length` nom 3.0 | Overall Length D 3.00 BSC | D → body_length; extension lines on the moulded body edges (top view); Note 2 confirms D/E1 are body dims |
| 3.6 | `body_width` nom 3.0 | Molded Package Width E1 3.00 BSC | E1 → body_width |
| 3.7 | `overall_width` nom 4.9 | Overall Width E 4.90 BSC | E's extension lines reach past the body to the lead tips (top view) → tip-to-tip → overall_width |
| 3.8 | `height` max 1.1 | Overall Height A –/–/1.10 | A → height; dashes in MIN/NOM ⇒ max only |
| 3.9 | `body_thickness` 0.75/0.85/0.95 | Molded Package Thickness A2 | A2 → body_thickness; three values ⇒ min/nom/max |
| 3.10 | `standoff` 0.0–0.15 | Standoff A1 0.00/–/0.15 | A1 → standoff (body underside to seating plane, side view) |
| 3.11 | `lead_width` 0.22–0.40 | Lead Width b 0.22/–/0.40 | b → lead_width (one lead's width, bottom view) |
| 3.12 | `lead_length` 0.40/0.60/0.80 | Foot Length L | L spans the flat foot from bend to tip (front view, 600 dpi); L1 "Footprint" 0.95 REF is the body-face-to-tip span and is REF besides — correctly excluded per the reference's explicit L1 rule. Foot reading is right. |
| 3.13 | `lead_thickness` 0.08–0.23 | Lead Thickness c 0.08/–/0.23 | c straddles the lead material at the bend (front view) |

Also checked and correctly left out: Foot Angle φ 0°–8° (no dimension name models an
angle), L1 0.95 REF, "Number of Pins N" (not a size), and `overall_length` (the only
along-rows callout is D, the body — the reference says leave it out rather than name D
twice).

### Item 3.14 — status policy: all 13 dimensions `inferred` — verdict: **GOLD**

reference.md: "An `extracted` dimension has to be readable from its own quote: one of
min/nom/max appears among the numbers the quote carries." On pages 40–41 the digits exist
in the text layer only as control bytes (`\x13`=0, `\x11`=.), so no quote can satisfy that
bar — `extracted` is impossible and `inferred` is the honest, skill-mandated mark ("the
checker does not test it"). The byte-exact garbled rows are on-page page-local anchors; for
page 41, whose drawing text extracts not at all, the footer row is the only byte-exact
anchor available. The review documents this deviation from ideal evidence openly. The
alternative (dropping all 13 dims) would be worse, and quoting decoded ASCII like
"Overall Height A 1.10" would fail `check_quotes` because the decode is not on the page
(run1's own intermediate files show exactly that dead end).

### Item 3.15 — quote byte-exactness — verdict: **GOLD**

`kicad-partspec validate` on the gold: **passed, zero non-warning findings** — 16 warnings,
all `status.inferred`, none `quote_not_found`. Independently re-checked all 13 dimension
quotes and 8 pin quotes with a whitespace-normalized substring scan of the cited pages'
`pdftotext -layout` output: all present. The run builds and gold build also passed with 0
failures.

### Item 3.16 — DFN-8 exclusion — verdict: **GOLD**

PDF page 38 = DFN outline, drawing C04-123C (decoded table: e 0.50 BSC, A 0.80/0.90/1.00,
A1 0.00/0.02/0.05, A3 0.20 REF, D 2.00 BSC, E 3.00 BSC, D2 1.30–1.55, E2 1.50–1.75, b
0.20–0.30, L 0.30–0.50, EXPOSED PAD in the view); PDF page 39 = DFN land pattern, drawing
C04-2123B (rendered: Optional Center Pad W2 1.45 / T2 1.75, C1 2.90, X1 0.30, Y1 0.75, G
0.20). None of these numbers appears anywhere in the gold; `exposed_pad` is `false`,
`pin_count` 8, no ninth pin. Page 41 is the only MSOP land pattern and pages 38–41 are the
complete drawing set (verified page-by-page through the end notes/appendices). Nothing
leaks in.

### Item 3.17 — `mpn` MCP9808-E/MS — verdict: **GOLD**

Product Identification System (PDF page 49, printed footer "DS25095A-page 51"; PDF index
and printed number coincide for all pages the gold cites — 1, 11, 38–41): example b)
"MCP9808-E/MS: Extended Temperature 8LD MSOP package", MS = "Plastic Micro Small Outline
(MSOP), 8-lead". Example d) `MCP9808T-E/MS` is the tape-and-reel sibling (`MCP9808T` =
Tape and Reel) and is correctly not recorded; the gold's string is the exact printed
orderable. `datasheet.revision` "Revision A (October 2011)" is printed verbatim in Appendix
B (PDF page 47). `manufacturer` "Microchip Technology Inc." matches the cover/footer.
`datasheet.url` is an optional field whose value is not printed inside the PDF (standard
Microchip DeviceDoc form of the doc number) — recording it is allowed and harmless; the
runs' omission is equally allowed.

### Item 3.18 — land values vs KiCad's JEDEC-derived numbers — verdict: **GOLD**

`/usr/share/kicad/footprints/Package_SO.pretty/MSOP-8_3x3mm_P0.65mm.kicad_mod`: 8 pads,
size 1.625 × 0.4, rows at ±2.1125 → 4.225 span — the review's cited KiCad numbers are
accurate. reference.md is explicit that `land_*` comes only from the datasheet's example
land pattern, so the gold keeping Microchip's own 4.40 / 1.45 / 0.45 over KiCad's
JEDEC-derived 4.225 / 1.625 / 0.4 is the ruled choice, and the review records the
disagreement instead of silently matching KiCad. Reproduced build: the gold generates
`MSOP-8_3.0x3.0mm_P0.65mm.kicad_mod` with pads 1.45 × 0.45 at ±2.2 (span 4.40) — the
datasheet's own pattern, 0 failures, no `footprint.skipped`.

### Gold audit summary

No gold error found in any pin (number, name, type, status, group, quote) or dimension
(values, min/nom/max split, status, quote), nor in `mpn`, `manufacturer`, `family`,
`pin_count`, `exposed_pad`, `sha256` or `revision`. The gold's one soft spot — page-41
quotes that carry no numbers — is permitted for `inferred` dimensions by the letter of
reference.md, is the only on-page byte-exact anchor the page offers, and is documented in
the review rather than hidden. The gold's build claim in the review reproduces exactly.

---

## Attribution of the scorer's symbol/footprint report (beyond the land items)

- **Symbols identical (pin level): true.** All three specs have byte-identical pin arrays
  modulo quote whitespace. Generated symbol files differ only in: `Footprint` property
  (gold `partspec:MSOP-8_3.0x3.0mm_P0.65mm` vs empty in both runs — downstream of the land
  dims), `Datasheet` property (gold's `datasheet.url` vs empty — the optional field the
  runs omit), and, run1 only, `Description` ("Microchip Technology" vs "…Inc." — the
  truncated manufacturer string). No pin-derived difference exists.
- **Footprints differ: one cause.** The gold's three `land_*` dimensions (page 41,
  C04-2111A) generate the footprint; the runs' absence of them emits `footprint.skipped`.
  Verified by building all three specs into `/tmp`. `datasheet.url` affects only the
  symbol's Datasheet property, never the footprint.

## Verdict inventory (items counted by the tally)

1. `land_span` 4.40 nom (p41, C) — GOLD · 2. `land_pad_length` 1.45 max (p41, Y1) — GOLD ·
3. `land_pad_width` 0.45 max (p41, X1) — GOLD · 4. pins 1–8 numbers/names/quotes — GOLD ·
5. pin types/statuses — GOLD · 6. group/alt_names absence — GOLD · 7. `pitch` 0.65 — GOLD ·
8. `body_length` 3.00 — GOLD · 9. `body_width` 3.00 — GOLD · 10. `overall_width` 4.90 —
GOLD · 11. `height` 1.10 max — GOLD · 12. `body_thickness` 0.75/0.85/0.95 — GOLD ·
13. `standoff` 0.00–0.15 — GOLD · 14. `lead_width` 0.22–0.40 — GOLD · 15. `lead_length`
0.40/0.60/0.80 (foot; L1 excluded) — GOLD · 16. `lead_thickness` 0.08–0.23 — GOLD ·
17. 13× `inferred` status policy + quote anchors — GOLD · 18. decode story + quote
byte-exactness — GOLD · 19. DFN-8 exclusion (p38/p39/EP 9) — GOLD · 20. `mpn`
MCP9808-E/MS (+revision/manufacturer/url policy) — GOLD.

TALLY: GOLD 20 · RUN 0 · BOTH 0 · NEITHER 0

GOLD CORRECTIONS: none

