# Review — lm393b_soic8 (TI LM393B, SOIC-8, drawing D0008A)

Gold standard for the LM393B in the SOIC (D) package of TI SLCS005AH
(LM393B, LM2903B, LM193, LM293, LM393 and LM2903 Dual Comparators).
Source PDF: `~/datasheets/lm393b_soic8.pdf`, sha256
`f28830c2f4cbd9ef6a1cd6788a840fa2b92caafee366d53385f88d1cf24e9456`, 56 pages.
Pages used: 3 (pinout figure + pin functions table), 26 (orderable addendum),
43 (PACKAGE OUTLINE D0008A), 44 (EXAMPLE BOARD LAYOUT / LAND PATTERN for D0008A).

## KiCad disagreements

Official KiCad symbol `LM393` (`/usr/share/kicad/symbols/Comparator.kicad_sym`;
it `extends "LM2903"`, which carries the pins) vs gold, per pin:

| Pin | Datasheet (Fig 4-1 / Table 4-1) | KiCad LM393 | Field | Decision |
|---|---|---|---|---|
| 1 | 1OUT, Output | `~`, open_collector | name / type | name: datasheet wins (`1OUT`). Type agrees structurally; gold `open_collector`, status `inferred` (type not printed in the I/O column; §6.1 Overview: "The open-collector outputs allow the user to level shift…") |
| 2 | 1IN-, Input | `-`, input | name / type | name: datasheet wins. Type agrees |
| 3 | 1IN+, Input | `+`, input | name / type | name: datasheet wins. Type agrees |
| 4 | GND, — | `V-`, power_in | name / type | name: datasheet wins. Type: gold `power_in`, `inferred` (ground pin, I/O column prints "—") |
| 5 | 2IN+, Input | `+`, input | name / type | name: datasheet wins. Type agrees |
| 6 | 2IN-, Input | `-`, input | name / type | name: datasheet wins. Type agrees |
| 7 | 2OUT, Output | `~`, open_collector | name / type | same treatment as pin 1 |
| 8 | VCC, — | `V+`, power_in | name / type | name: datasheet wins. Type: gold `power_in`, `inferred` |

Pin numbers and pairing agree 8/8. KiCad's names are deliberately generic
(the symbol serves the whole LMx93 family); the datasheet names win in the gold.

Official footprint `SOIC-8_3.9x4.9mm_P1.27mm`
(`/usr/share/kicad/footprints/Package_SO.pretty/`) vs gold dimensions:

| Item | Datasheet (D0008A / land example) | KiCad footprint | Decision |
|---|---|---|---|
| pitch | 1.27 (6X .050 [1.27]) | 1.27 (pads at ±1.905, ±0.635) | agree |
| body | 3.81–3.98 × 4.81–5.00 mm | 3.9 × 4.9 (F.Fab outline) | agree at nominal |
| land pad size | 1.55 × 0.6 | 1.95 × 0.6 | pad width agrees exactly; pad length disagrees: KiCad pads are 0.4 mm longer (IPC gull-wing generator default). Gold records TI's 1.55 — the datasheet's own land pattern wins |
| pad row span (center-to-center) | 5.4 ((.213) [5.4]) | 4.95 (pads at x = ±2.475) | disagreement: gold records 5.4 from TI's land example. Note the outer tip-to-tip extent effectively agrees: TI 5.4 + 1.55 = 6.95 vs KiCad 4.95 + 1.95 = 6.9 — the difference is only how far the pad extends outward vs inward |
| exposed pad | none for SOIC (Thermal Pad row is DSG-only) | none | agree |

Generated footprint from this gold (pads 1.55 × 0.6 at x = ±2.7) therefore
differs from the official KiCad footprint in pad length and row span — recorded
here as evidence, not as a defect of either side.

## Values that had to be interpreted

- `standoff` 0.11–0.25 (`.004-.010`): in DETAIL A this dimension's two arrows
  were traced at pixel level (600 dpi render): the down-arrow tip touches the
  extension line collinear with the moulded body's bottom edge, the up-arrow
  tip touches the line collinear with the lead foot's bottom (the seating
  plane). That is the body-underside-to-seating-plane gap, i.e. the standoff
  (letter-table A1). Marked `extracted` because the span was verified on the
  rendered image; noted here because DETAIL A is schematic, not to scale.
- `lead_thickness` 0.13–0.25 (`.005-.010 TYP`): taken from the end view, where
  the two arrows straddle the flat foot's top and bottom surfaces — the lead
  cross-section in a side view, per the reference's three-lead-callout rule.
  `TYP` means all leads share the value; a range, so min/max are recorded.
- Orientation of body_length vs body_width: the D0008A top view is drawn
  rotated (pins 1–4 down the left side). Along the pin rows the moulded body
  measures .189-.197 [4.81-5.00] (NOTE 3) → `body_length`; across the rows
  .150-.157 [3.81-3.98] (NOTE 4) → `body_width`. Both verified by extension
  lines landing on body edges, not lead tips. Consistent with the package
  name 3.9 × 4.9 and the Device Information table (4.90 × 3.91 body).
- `pitch` 1.27 is a boxed (basic) callout `6X .050 [1.27]`; recorded as `nom`
  like the reference's BSC pitch example. The 6X count covers the three gaps
  on each of the two rows (drawn once, between the pin 8 and pin 7
  centerlines — verified on the 300 dpi render).
- Quotes for body_length, body_width, overall_width, height, lead_width and
  standoff are single tokens (e.g. `.189-.197`, `.069 MAX`) because the text
  layer interleaves tokens from neighbouring callouts; the millimetre brackets
  were read and confirmed on the rendered page (the skill's hint-based fallback).

## Deliberately left out

- Boxed `.010 [0.25]` in DETAIL A (page 43): a boxed basic dimension whose
  leader-arrow pair spans the dashed reference line down to the seating plane.
  The dashed line sits between the foot's top surface and the body underside
  on the schematic detail, so the callout is either the basic standoff or the
  basic lead thickness — the drawing cannot decide which (it is not to scale;
  the dashed line is ~0.04 mm above one and ~0.07 mm above the other at detail
  scale). It pairs with the position feature control frame
  `⊕ .010 [0.25]Ⓜ C A B` (same value), which marks it as a GD&T basic, not a
  size to record. Both candidate dimensions are already recorded from
  unambiguous callouts (`.004-.010` standoff, `.005-.010 TYP` thickness).
- Boxed `.004 [0.1] C` beside SEATING PLANE (page 43): the gage-plane offset
  (datum C artifact), not a standoff.
- `2X .150 [3.81]` (page 43): span between the centerlines of the first and
  last lead of one row (3 × 1.27), boxed basic, 2X both rows — a lead
  centre-to-centre span is not recorded.
- `(.041) [1.04]` (page 43): parenthesized reference dimension (lead tip to
  body edge) in DETAIL A.
- `4X (0°-15°)` (twice) and `0°-8°` (page 43): lead splay angles, not sizes.
- `overall_length`: no callout measures tip-to-tip along the pin rows (the
  leads do not protrude beyond the body in that direction on this drawing);
  left out rather than named from a body dimension.
- `body_thickness`: no separate body-thickness (A2) callout on D0008A.
- `land_ep_size` / exposed pad: the SOIC has none; Table 4-1's Thermal Pad row
  applies to the DSG (WSON) package only (SOIC column prints "—").
- Page 44 solder-mask details (`.0028 MAX/MIN [0.07] ALL AROUND`, the SOLDER
  MASK OPENING rectangles): mask, not metal. `(R.002) TYP [0.05]`: pad corner
  radius, not a pad size.

## Contradictions inside the datasheet

- Dash characters of the input names: Figure 4-1 prints `1IN−` / `2IN−`
  (U+2212 MINUS SIGN); Table 4-1 prints `1IN–` (U+2013 EN DASH) for pin 2 but
  `2IN-` (ASCII hyphen) for pin 6. Gold names normalize to the ASCII hyphen
  (`1IN-`, `2IN-`) per the skill; the quotes keep the table's own characters.
- Table 4-1's DSG column and Figure 4-2 belong to the WSON package: `V+`
  instead of `VCC`, and the thermal pad (`PAD`, "Connect directly to GND
  pin"). These are another package's names, not `alt_names` of the SOIC part;
  no alt_names are recorded anywhere in this gold.
- Device Information (page 1) gives the SOIC body as "4.90mm x 3.91mm" while
  D0008A's nominal is 3.90 (range 3.81–3.98). The 3.91 looks like a rounding
  slip; both sit inside the drawing's range, and the drawing wins.

## Coverage of the verification

- Pin pairing: Figure 4-1 verified on the rendered page 3 image (150 dpi):
  1OUT=1, 1IN−=2, 1IN+=3, GND=4 down the left; VCC=8, 2OUT=7, 2IN−=6, 2IN+=5
  down the right. Quotes taken from Table 4-1 rows on the same page.
- Dimensions: every callout on page 43 traced on renders at 110 dpi (whole
  page), 300 dpi (five region crops), 600 dpi (DETAIL A) and 1200 dpi (left
  arrow cluster of DETAIL A); the standoff arrows were additionally verified
  by pixel scans (arrow tips touch the body-underside extension line at
  y≈618 and the seating-plane line at y≈673 in the 600 dpi render).
  Land pattern callouts verified on the rendered page 44 at 300 dpi: pad
  length horizontal (along the lead direction), pad width vertical, span
  between the two pad-column centerlines, all dimensioned on the exposed
  metal ("EXPOSED METAL SHOWN").
- `kicad-partspec validate --datasheet`: passed, `failed` = [] (4 warnings,
  all `status.inferred` on pins 1/4/7/8 — the honest open-collector and
  supply typings).
- `kicad-partspec build`: passed, 0 failures; symbol
  `LM393BIDR.kicad_sym` and footprint
  `partspec.pretty/SOIC-8_3.9x4.9mm_P1.27mm.kicad_mod` both generate (no
  `footprint.skipped` — the land pattern is complete) and both load cleanly
  under `kicad-cli` 9 (`sym upgrade` / `fp upgrade` exit 0).

## mpn

The sheet is a family datasheet (LM393B/LM2903B/LM193/LM293/LM393/LM2903
across SOIC, VSSOP, PDIP, SO, TSSOP, SOT-23, WSON). The orderable addendum
(page 26) lists for the SOIC (D) package: `LM393BIDR` — "Active, Production,
SOIC (D) | 8, 2500 | LARGE T&R, NIPDAU, Level-1-260C-UNLIM, -40 to 85 °C,
marking LM393B" — plus the `.A`/`.B` material variants and `G4` variants of
the same number. No page prints a bare `LM393BID`, so the tape-and-reel
suffix stays. Gold `mpn` = `LM393BIDR`; `manufacturer` = `Texas Instruments`.
Revision string copied from the page-1 header as printed:
`SLCS005AH – OCTOBER 1979 – REVISED APRIL 2025`; URL
`https://www.ti.com/lit/ds/symlink/lm393b.pdf`.
