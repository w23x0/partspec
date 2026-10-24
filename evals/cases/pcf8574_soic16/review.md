# Review: pcf8574_soic16 (TI PCF8574, DW / SOIC-16, drawing DW0016A)

Source: `~/datasheets/pcf8574_soic16.pdf` (TI SCPS068K, sha256 `9f2c7693…a8079`, 39 pages).
Scope: base PCF8574 only (not PCF8574A) and only the DW (SOIC, 16 pins) package; the same PDF
documents DGV/PW (TSSOP-20), RGY (VQFN-20), RGT (VQFN-16), N (PDIP-16) — their pins and
drawings are out of scope. The pinout of the base part and the A variant is identical; the A
variant differs in I2C address range only, and its content (e.g. `PCF8574A` orderables) was not used.

## KiCad disagreements

Cross-check targets: symbol `PCF8574T` in `/usr/share/kicad/symbols/Interface_Expansion.kicad_sym`
(there is no symbol named exactly `PCF8574`; `PCF8574T` and `PCF8574P` are the base variants and
both extend `TCA9534`, whose pin block carries the shared pinout; `PCF8574T`'s default footprint is
`Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm`). Footprint: the task named
`SOIC-16_7.5x10.3mm_P1.27mm.kicad_mod`; no such file exists in
`/usr/share/kicad/footprints/Package_SO.pretty/` — the actual file (and the one the symbol
references) is `SOIC-16W_7.5x10.3mm_P1.27mm.kicad_mod`, which was used.

| Item | Datasheet (SCPS068K) | KiCad | Decision and basis |
|---|---|---|---|
| Pin 1–16 pairing | A0=1, A1=2, A2=3, P0=4, P1=5, P2=6, P3=7, GND=8, P4=9, P5=10, P6=11, P7=12, INT=13, SCL=14, SDA=15, VCC=16 (Figure 4-4, Table 4-1 "DW or N" column) | identical (TCA9534 base block) | Agreement — all 16 numbers and names pair the same. |
| Pin 13 name | `INT` | `~{INT}` | Keep `INT`, no `alt_names`. The datasheet prints plain `INT` (Figure 4-4 and Table 4-1); `~{INT}` is KiCad's active-low notation of the same function, not a different name. Gold records the datasheet. |
| Pin 16 name | `VCC` | `VDD` | Keep `VCC`. KiCad's base symbol is drawn for the TCA9534 family (which names the supply `VDD`); this datasheet prints `VCC` everywhere (Figure 4-4, Table 4-1, absolute-maximum table). |
| Pin 13 electrical type | TYPE column "O"; description "Interrupt output. Connect to VCC through a pullup resistor"; feature list "Open-drain interrupt output" | `open_collector` | Agreement in effect: open-drain output → `open_collector`, status `inferred` per the reference type table. |
| Types of all other pins | I / I/O / — | `input` / `bidirectional` / `power_in` | Agreement — KiCad's choices match the reference's mapping for all 16 pins. |
| Footprint pitch | 1.27 (14X boxed callout, outline p.36; 14X (1.27), land p.37) | pads 1.27 apart | Agreement. |
| Land pattern pad span | (9.3) centre-to-centre (p.37) | pads at x=±4.65 → 9.3 | Agreement — exact. |
| Land pad width | (0.6) (p.37) | 0.6 | Agreement — exact. |
| Land pad length | (2) (p.37) | 2.05 | Disagreement of 0.05 mm: KiCad's gull-wing generator extends the pad for IPC fillet; TI's example land pattern prints (2). Gold keeps the datasheet's (2). |
| Body size | 7.4–7.6 × 10.1–10.5 mm (E1 NOTE 4, D NOTE 3) | fab outline 7.5 × 10.3 | Agreement at nominal (7.5, 10.3 are inside the printed ranges). |
| Across-rows lead-tip span | 9.97–10.63 ("10.63 TYP / 9.97") | no explicit counterpart (courtyard ±5.93 includes fillet allowance) | No conflict: nominal 10.3 agrees with the JEDEC MS-013 package the KiCad footprint description cites. |
| Height, standoff, lead width/thickness/length | 2.65 max / 0.10–0.30 / 0.31–0.51 / 0.10–0.33 / 0.40–1.27 | not stated in the .kicad_mod (embodied in the 3D model/JEDEC defaults) | Nothing to disagree with; JEDEC MS-013 registration is cited by both. |

## Values that had to be interpreted

- `standoff` 0.10–0.30 (status **inferred**). DETAIL A prints the value as an unlabeled `0.3 / 0.1`
  callout. Three candidate readings existed for its upper extension line: the body underside, the
  foot's top surface, or the dotted gage plane. Traced at 600 dpi with pixel-column scans: the
  upper line is solid and horizontal at the height of the body underside, while the gage plane is a
  *dotted* line a small step below it (drawn at the max-standoff condition: 0.30 above the seating
  plane = 0.05 above the boxed 0.25 gage plane, matching the drawn step); the foot's top surface
  slopes (0°–8°) and does not extend to the callout. Lower line = the seating plane, which spans the
  whole view. So the callout spans body underside → seating plane = the standoff. Marked `inferred`
  because the drawing does not name the callout and the attribution needed forensic tracing, not a
  plain read.
- `lead_thickness` 0.10–0.33 (status `extracted`). The side-view callout `0.33 / 0.10 TYP` is the
  near-twin of DETAIL A's `0.3 / 0.1` and the easiest misread on the sheet (swap the two and
  standoff becomes 0.10–0.33 and thickness 0.10–0.30). Decided by the reference's rule — name the
  span by its two planes: the side-view extension lines start at the foot's top and bottom faces and
  run parallel (both following the drawn foot tilt), arrows straddling the lead material itself = the
  lead's cross-section; DETAIL A's pair runs body-underside → seating plane (see above). No letter
  labels exist on TI drawings, so this is a plain extension-line read once rendered at 600 dpi, hence
  `extracted`.
- `pitch` 1.27 from the boxed `14X 1.27` callout. **Tension documented**: the reference's boxed-basic
  paragraph says a boxed basic value is "not a size: never record it as `standoff`, `lead_length`,
  `lead_thickness` or anything else", while the same reference's letter table maps `e` → `pitch` and
  its example records `"e 0.95 BSC"` — BSC is basic. The boxed-basic prose targets gage-plane offsets
  and land-pattern basics (both excluded here, see below); the pitch is a real size printed basic on
  every vendor's outline. Following the reference prose as authoritative, the letter-table/example
  reading wins for `e`: pitch recorded, `extracted`.
- `overall_width` 9.97–10.63 carries a `TYP` label on a stacked pair. Per the reference, two numbers
  stacked on the drawing give `min` and `max` (the `TYP` belongs to the nominal between them); both
  printed values are recorded.
- `lead_length` 0.40–1.27 from DETAIL A's `1.27 / 0.40`. Its extension lines run from the lead toe to
  the start of the bend (the heel of the flat foot) — the reference's definition of `lead_length`.
  The adjacent `(1.4)` spans toe → body face, which the reference explicitly excludes ("the lead
  length from the body face to the tip … is not our `lead_length`") and is parenthesised anyway.
- Land pattern values 16X (2), 16X (0.6), (9.3) are all parenthesised reference dimensions. The
  reference allows parenthesised values *for `land_*` only*; all three are recorded as `land_*`
  (`extracted`), and none entered the package dimensions. `(9.3)` was verified on the rendered page
  to run between the two pad-column *centre*lines (dash-dot lines), so it is `land_span`
  centre-to-centre, not an outer-edge span.
- Pin `group` for P0–P7: each port I/O is grouped under its own printed channel name (`P0`…`P7`).
  The datasheet presents eight repeated, identical quasi-bidirectional I/Os with printed channel
  names — the reference's "channel names CH0–CH7" pattern; each channel happens to be one pin.
  A0–A2 stay ungrouped (the reference names address pins as pins with no unit of their own); SCL,
  SDA, INT have no unit. GND/VCC: the reference makes grouping a bare VDD/VSS pair `power`
  *optional* when the TYPE column does not print a supply block — Table 4-1 prints `—` for both, so
  `group` is left off.
- Pin types: `power_in` for GND/VCC and `open_collector` for INT are chosen through the reference's
  supply/open-drain rows (TYPE column prints `—`/`O`), hence pin status `inferred`. The open-drain
  evidence is on page 1 (feature list "Open-drain interrupt output"); the pin's own quote stays on
  page 3 where the pin is printed. All other pin statuses are `extracted` (number/name verified on
  the rendered Figure 4-4, type read from Table 4-1's TYPE column).

## Deliberately left out

- `overall_length` — the drawing prints no tip-to-tip callout along the rows. The only along-rows
  callout is 10.5/10.1 (NOTE 3), whose extension lines land on the moulded body edges (verified at
  300 dpi: both extension lines touch the body outline, not the pin-1/pin-8 lead ends), so it is
  `body_length`. Per the reference: leave `overall_length` out rather than rename a body dimension.
- Boxed `2X 8.89` — the span between the end-lead centre-lines of one row (7 × 1.27); a lead
  centre-to-centre span is explicitly not recorded by the reference.
- Boxed `0.25 GAGE PLANE` (DETAIL A) — a gage-plane offset, not a standoff.
- Boxed `0.1 C` and datums `C`, `A`, `B` (end view / top view) — datum references, not sizes.
- `⊕ 0.25Ⓜ C A B` — a positional-tolerance feature control frame, not a dimension.
- `0°–8°` — the lead bend angle; not a linear dimension in the name list.
- `(1.4)` — parenthesised reference span (toe → body face); see `lead_length` above.
- `R0.05 TYP` — land pad corner radius; no dimension name for it.
- Solder-mask details on p.37 (`0.07 MAX/MIN ALL AROUND`) — mask opening relative to the metal, not
  the pad; the reference forbids substituting mask for pad. The pad rectangles in the land pattern
  are plain metal (labelled `METAL` in the details), so 16X (2) / 16X (0.6) / (9.3) are the metal.
- Page 38 (`EXAMPLE STENCIL DESIGN`, same DW0016A) — stencil apertures are not the example land
  pattern; not a source for `land_*`.
- `body_thickness` — DW0016A prints no body-without-leads callout (no A2 row); height is only
  2.65 MAX overall.
- `land_ep_size` — the DW has no exposed pad (`exposed_pad: false`).
- Everything for the other packages in this PDF: PW0020A (TSSOP-20, p.27–29), RGT0016C (VQFN-16,
  p.32–34), the N (PDIP) pinout shares Table 4-1's "DW or N" column but has no drawing in this PDF,
  and DGV/RGY (20-pin) columns of Table 4-1. Only the DW column and pages 36–37 were used.
- All PCF8574A content (address-range tables, A-variant orderables such as `PCF8574ADWR`).

## Contradictions inside the datasheet

- **Figure 4-4 caption prints "20 Pins"**: "Figure 4-4. DW or N Package, 20 Pins, Top View" — the
  figure itself shows exactly 16 pins, §5.4's thermal table lists "DW … 16 PINS", the cover's Package
  Information lists "SOIC (DW, 16)", and drawing DW0016A shows 16 leads. The caption is a typo; 16
  is used everywhere.
- **Cover Package Information vs the outline**: the cover prints SOIC (DW, 16) package size
  "10.3mm × 10.3mm" (length × width, nominal, including pins). The outline gives body length
  10.1–10.5 (nom 10.3) and across-rows tip-to-tip 9.97–10.63 (nom 10.3) — consistent once rounded;
  the cover's "10.3 width" is the lead-tip span, not the 7.5 body width. No action needed; recorded
  here because the coincidence of two 10.3s invites misreading body_width as 10.3.
- **Table 4-1 TYPE column prints `—` for GND and VCC** while the description text and §3 make them
  the supply/ground. Handled by the reference's supply rule (`power_in`, `inferred`), not a defect.
- **Table 4-1 row `P[0..7]` prints two interleaved number groups** ("4, 5, 6, 7," / "9, 10, 11," /
  "12" for the DW or N column); the text-layer rendering of that cell is garbled by column
  interleaving with the other package columns. The pairing was taken from Figure 4-4 (verified on
  the rendered image) and is consistent with the table's DW numbers.

## Coverage of the verification

- sha256 computed with `sha256sum` (matches the `9f2c7693…` prefix).
- Page discovery by `pdftotext -layout` over the whole document; pin table + Figure 4-4 on page 3;
  DW0016A outline on page 36, EXAMPLE BOARD LAYOUT (land pattern) on page 37, stencil on page 38;
  package-option addendum on pages 24–25.
- **Every pin pairing rendered and checked**: page 3 rendered at 300 dpi and Figure 4-4 cropped —
  all 16 number↔name pairs read off the image (left column A0…GND = 1…8, right column
  VCC…P4 = 16…9); the pin-4 label `P0` sits one text row below its number in the text layer, which
  is why pin 4's quote spans both rows ("4 13 INT P0").
- **Every dimension callout rendered and checked**: page 36 at 150 dpi (whole sheet), 300 dpi crops
  of the top callout (10.63/9.97 across lead tips), left callout (10.5/10.1 on body edges), bottom
  callout (7.6/7.4 on body edges), right callouts (14X 1.27 between adjacent lead centre-lines; 2X
  8.89 between end-lead centre-lines; 16X 0.51/0.31 straddling the lead), end view (2.65 MAX); page
  36 at 600 dpi with pixel-column scans for the side-view `0.33/0.10 TYP` (parallel lines from the
  foot's two faces = lead cross-section) and DETAIL A's `0.3/0.1` (body underside → seating plane),
  `0.25 GAGE PLANE` (dotted plane), `1.27/0.40` and `(1.4)` (toe→bend-start vs toe→body-face, three
  vertical extension lines identified: toe, bend start, body face).
- **Land pattern rendered**: page 37 at 150 dpi (whole sheet) and 300 dpi crops — 16X (2) spans the
  pad's long (lead-direction) edges, 16X (0.6) straddles the pad's short edges, 14X (1.27) runs
  between adjacent pad centre-lines, (9.3) runs between the two column centre-lines (dash-dot).
- Quotes built from `pdftotext -layout` token order; where labels interleave (`10.63 SEATING PLANE
  TYP 9.97`, `7.6 B 0.25 C A B 2.65 MAX 7.4 NOTE 4`, `0.3 0 -8 0.1`), the quote carries the page's
  own token stretch so it both matches the checker and shows the callout to a human.
- `kicad-partspec validate --datasheet`: **passed, `failed` empty**; 4 warnings, exactly the four
  deliberate `inferred` statuses (pins GND, INT, VCC; dimension standoff).
- `kicad-partspec build`: **passed** — symbol `PCF8574DW.kicad_sym` and footprint
  `SOIC-16_7.5x10.3mm_P1.27mm.kicad_mod` generate (no `footprint.skipped`: the datasheet's land
  pattern is complete). Generated pads sit at x=±4.65, 1.27 pitch, 2×0.6 — directly comparable with
  KiCad's official `SOIC-16W_7.5x10.3mm_P1.27mm` (±4.65, 1.27, 2.05×0.6).

## mpn

The gold records **`PCF8574DW`**. The package-option addendum (pages 24–25) lists, for the SOIC (DW)
16-pin package: `PCF8574DW` (Obsolete), `PCF8574DWR` (Active, tape-and-reel), plus `.A`/`G4`
orderable variants (`PCF8574DWR.A`, `PCF8574DWR1G4`, `PCF8574DWRG4`). The reference says the mpn is
the orderable the addendum lists, but a tape-and-reel suffix may be dropped "only when the page
prints the shorter number" — and this page does print `PCF8574DW` itself, so the shorter package
form is used rather than the T&R-only `PCF8574DWR`. `PCF8574DW` is also the form that matches the
mechanical drawing code (DW0016A) and the part marking ("PCF8574"). No temperature suffix exists on
any DW orderable. The A-variant orderables (`PCF8574ADW*`) are a different part and were not
considered. The datasheet's title/cover print the base number as `PCF8574`; the package-bearing
`PCF8574DW` is the most specific part number the datasheet actually prints for this package, which
is what the reference demands (a form that appears on a page, not a constructed one).

## Notes for the grader

- 16 pins, 12 dimensions (9 package + 3 land). Inferred: standoff (dimension) and the GND/INT/VCC
  pin types — each documented above. Everything else is `extracted` with a page-anchored quote.
- The KiCad footprint file to compare against is `SOIC-16W_7.5x10.3mm_P1.27mm.kicad_mod` (the task's
  `SOIC-16_7.5x10.3mm_P1.27mm.kicad_mod` does not exist in this library installation); the symbol to
  compare against is the `TCA9534` base block behind `PCF8574T`/`PCF8574P` (no literal `PCF8574`
  symbol exists).

## Correction — 2026-10-24 (round-6 adjudication, [GOLD])

**What changed:** the eight `group` keys `P0`…`P7` on pins 4–7 and 9–12 were removed; those pins
are now ungrouped, like every other pin of this part.

**Why:** the datasheet presents P0–P7 as the bits of **one** 8-bit quasi-bidirectional I/O port —
page 1 "8-bit quasi-bidirectional I/O port (P0–P7)", Table 4-1's single row `P[0..7]`
("P-port input/output"), Figure 7-2 "Each P-Port Input or Output" — and the word "channel"
appears nowhere in SCPS068K (grep-verified). reference.md's group rule keys on the datasheet's
own units ("the key is whatever the datasheet calls the unit"); the corpus's accepted golds for
identical structures (74hc595's Q0–Q7, mcp23008's GP0–GP7) leave port bits ungrouped. The
original gold imported a channel vocabulary this datasheet does not use. Found by the round-6
adjudicator; both runs had left these pins ungrouped and were scored wrong against the original
gold. Contrast mcp3008, whose CH0–CH7 the datasheet itself names channels and whose gold grouping
the round-6 adjudication upheld.
