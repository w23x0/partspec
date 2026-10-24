# Gold review — mcp3008_soic16

Gold PartSpec for the Microchip MCP3008, 16-lead SOIC ("16-Lead Plastic Small
Outline (SL) — Narrow, 3.90 mm Body [SOIC]", Microchip Technology Drawing
C04-108B, PDF page 32 of DS21295D). The datasheet documents MCP3004 and
MCP3008 in PDIP/SOIC/TSSOP; everything here is the MCP3008 in its 16-lead SOIC
package only.

Datasheet: `~/datasheets/mcp3008_soic16.pdf` (DS21295D),
sha256 `e6c2231de727395ff42b094ed4ffd185db77b3958ac0b805f97330f4ad4b1122`.

## The text-layer quirk on the drawing pages

Pages 27–32 (package drawings) are set in a custom font whose glyphs have no
Unicode mapping: `pdftotext -layout` returns control bytes where the digits
(and even the table row labels and the MIN/NOM/MAX header) sit. Verified
directly: page 32's text layer carries the drawing callout letters (`D`, `N`,
`E`, `E1`, `e`, `b`, `A`, `A2`, `A1`, `L`, `L1`, `h`, `c`, `α`, `β`, `φ`) in
ASCII, but **no ASCII digit anywhere** — the dimension values are unmapped
bytes. Consequences handled as follows:

- Every dimension value was read from a 300-dpi render of page 32
  (`pdftoppm -r 300`, cropped table) after a 150-dpi whole-page pass.
- Every dimension quote is the byte-exact `pdftotext -layout` row (whole
  document run, the same extraction `check_quotes` performs). The checker's
  whitespace normalization treats the same control bytes as whitespace on both
  the quote and the page, so each quote is found on page 32.
- As an independent check on the row-to-value alignment, the font's glyph map
  was reconstructed from the render (digits `0`–`9` → `\x04 \x1d \x03 \x2c
  \x17 \x30 \x3f \x05 \x3e \x18`, `.` → `\x14`, `°` → `\x42`, and the `BSC`/
  `REF` letter glyphs) and **all 16 table rows decoded to exactly the values
  visible in the render** — e.g. Pitch row → `1.27 BSC`, Standoff row →
  `0.10 – 0.25`, Lead Width row → `0.31 – 0.51`.
- One artifact worth knowing: the glyph for `1` is the byte `\x1d`, which
  Python (and the checker's `normalize()`) classifies as whitespace, so a
  trailing `1` disappears at a row edge (`0.51` ends in `1`). The same
  normalization runs on the page text, so quotes still match; the decode check
  above was run on the raw unstripped rows for this reason.

## KiCad disagreements

Cross-checked pin-by-pin against `MCP3008` in
`/usr/share/kicad/symbols/Analog_ADC.kicad_sym` (the symbol `extends
"MCP3208"`, so the pins were read from MCP3208) and against
`/usr/share/kicad/footprints/Package_SO.pretty/SOIC-16_3.9x9.9mm_P1.27mm.kicad_mod`.

| Where | KiCad | This gold | Decision and basis |
|---|---|---|---|
| Pin 12 type | `output` | `tri_state` (inferred) | Keep `tri_state`. The pin row says "Serial Data Out", but Figures 5-1/5-2 (page 20) print `HI-Z` on DOUT while CS is high, and §6.1 says "the output is at high-impedance for the first two clocks". The skill's rule: a pin the part can put in Z is `tri_state` even when its row says output (74HC595 case). |
| Pin 15 type | `power_in` | `passive` (inferred) | Keep `passive`. The datasheet prints "Reference Voltage Input", and the skill's mapping table sends "an analog reference" to `passive` with status `inferred`; VREF is the analog reference (§2.0 "Reference Input"; §5.1 note: "the reference input becomes a high-impedance node"), not a supply or ground. KiCad's `power_in` is a defensible library choice but the skill's row is specific to this case. |
| Pin 10 name | `~{CS}/SHDN` | `CS/SHDN` | Same label, different encoding: KiCad's `~{...}` is the overline escape and the datasheet prints an overline over CS (visible in the page-1 figure and Table 3-1 render). Recorded as the text layer prints it. Cosmetic, not a functional disagreement. |
| Pins 11/12/15/16 names | `Din`/`Dout`/`Vref`/`Vdd` | `DIN`/`DOUT`/`VREF`/`VDD` | KiCad mixes case to suggest the printed subscript (D-IN, D-OUT, V-REF, V-DD); the text layer prints `DIN`, `DOUT`, `VREF`, `VDD` and Table 3-1's Symbol column reads the same way on the render. Cosmetic. |

Everything else agrees exactly: pin numbers 1–16 and all 16 names match one
for one, and the electrical types of the other 14 pins match KiCad (CH0–CH7
`input`; DGND/AGND/VDD `power_in`; CS/SHDN and DIN and CLK `input`).

Footprint comparison: the official footprint's name (3.9×9.9 mm, P1.27 mm)
matches the datasheet's E1 = 3.90 BSC, D = 9.90 BSC, e = 1.27 BSC. Its pad
geometry (1.95×0.6 mm pads, 4.95 mm row span) is IPC-generator output — this
datasheet prints no 16-lead land pattern to compare against (see below), so
that geometry is neither confirmed nor contradicted here.

## Values that had to be interpreted

- **All ten dimensions are `inferred`.** Not because the values were derived —
  each was read from the rendered table — but because the skill requires an
  `extracted` dimension to be readable from its own quote ("one of
  min/nom/max appears among the numbers the quote carries"), and no ASCII-digit
  quote can be built from page 32's unmapped text layer. `inferred` is the
  honest flag: a human must confirm each against the render, which is exactly
  what the decode cross-check above documents. (The checker does not test
  `inferred` dimensions; marking them `extracted` would make `validate` fail
  SRC-006 with `dim.quote_unsupported`.)
- **D = 9.90 BSC recorded as `body_length`, not `overall_length`.** The row is
  labelled "Overall Length", but D's extension lines land on the molded body
  ends: a SOIC's leads protrude only on the two long sides, so there is no
  tip-to-tip callout along the rows, and note 3 groups D with E1 as the
  molded-body dimensions ("Dimensions D and E1 do not include mold flash").
  The skill's letter table maps `D` to `body_length`; `overall_length` is
  deliberately absent.
- **E = 6.00 BSC recorded as `overall_width`, E1 = 3.90 BSC as `body_width`.**
  E's extension lines land on the lead tips of both rows (tip-to-tip across
  the rows; 3.90 body + two ≈1.05 mm lead protrusions), matching the skill's
  "tip-to-tip E" row; E1 is the molded width.
- **A2 recorded as min 1.25 only.** The row prints `1.25 – –` (MIN, no NOM,
  no MAX) — verified at 300 dpi and consistent with the sibling 14-lead SOIC
  drawing C04-065B on page 28, whose A2 row prints the same `1.25 – –`.
  Recorded as printed, not "completed" from typical values.
- **L = 0.40–1.27 recorded as `lead_length`.** Microchip's "Foot Length" is
  the foot from the lead tip to the start of the bend — the skill's
  `lead_length` ("the foot: the flat part resting on the board"). L1 ("Footprint",
  1.04 REF, body-to-tip) is the other callout and is not recorded (see below).
- **DOUT `tri_state`, CLK `input`, both `inferred`.** DOUT: HI-Z evidence in
  Figures 5-1/5-2 and §6.1 (see disagreements table). CLK: no direction is
  printed for it anywhere (Table 3-1 says only "Serial Clock"), but §5.1 says
  "The first clock **received** with CS low…" and "the device continues to
  **receive** clocks" — the device receives clocks on this pin, so `input`,
  flagged `inferred` for human confirmation.
- **Groups.** CH0–CH7 are grouped `"CH0"`–`"CH7"` (numbered channels are units;
  the datasheet's own names are the keys). VDD/DGND/AGND are grouped `"power"`
  (the reference makes that optional for a bare supply/ground set; chosen here
  because the three pins are unambiguous supplies/grounds). CS/SHDN, DIN,
  DOUT, CLK and VREF stay ungrouped — a chip select, a serial port and the
  reference are not units.

## Deliberately left out

- **All `land_*` dimensions.** The datasheet's only example land pattern is on
  page 29: "8-Lead Plastic Small Outline (SN) — Narrow, 3.90 mm Body [SOIC]"
  (drawing C04-2057A; Contact Pitch 1.27 BSC, Contact Pad Spacing C 5.40,
  Contact Pad Width (X8) 0.60 MAX, Contact Pad Length (X8) 1.55 MAX — read
  from the render; that page's text layer is unmapped too). That is a package
  **neither MCP3004 nor MCP3008 is offered in**, with 8 pads, not 16. Borrowing
  it for the 16-lead part would be inventing from a sibling package, so no
  `land_pad_length`/`land_pad_width`/`land_span` exists. `build` correctly
  reports `footprint.skipped` ("add these dimensions with a source:
  land_pad_length, land_pad_width, land_span") — that is the honest outcome,
  not a defect to paper over.
- **h — "Chamfer (optional)", 0.25–0.50.** No chamfer name exists in the
  skill's dimension list.
- **L1 — "Footprint", 1.04 REF.** A REF (reference) dimension, and not the
  foot length (L is); no name in the list.
- **φ Foot Angle 0°–8°, α/β Mold Draft Angles 5°–15°.** Angles; no names.
- **N = 16** goes in `package.pin_count`, not into `dimensions`.
- **`overall_length`** — the drawing prints no tip-to-tip-along-the-rows
  callout (see body_length above); the skill says leave it out rather than
  rename a body dimension.
- **`alt_names` everywhere empty.** Table 3-1 prints exactly one symbol per
  pin. "CS/SHDN" is the printed compound name of one pin (§3.7 "Chip
  Select/Shutdown (CS/SHDN)"), not a name with an alternate. The MCP3004-only
  cells of Table 3-1 (pins 5,6 → NC) and the "5,6 – NC No Connection" row were
  not taken: they belong to the sibling part.

## Contradictions inside the datasheet

- None between the two pin sources: the page-1 "Package Types" figure
  (MCP3008, "PDIP, SOIC") and Table 3-1 (page 15) agree on all 16
  number↔name pairings.
- One oddity, recorded rather than resolved: the only land pattern in the
  drawing set (page 29) is for an 8-lead SOIC package the product identification
  system (page 37) never offers for either device. It looks like a drawing
  carried over from another datasheet; it is not used here (see above).
- A2's `1.25 – –` (MIN-only) row is unusual but is repeated verbatim on the
  14-lead SOIC drawing (page 28), so it is recorded as printed.

## Coverage of the verification

- `sha256sum` → `e6c2231d…` (recorded in `datasheet.sha256`).
- Pin pairing: page 1 rendered at 150 dpi (MCP3008 "PDIP, SOIC" figure) and
  page 15 rendered at 150 dpi (Table 3-1); every one of the 16 pairings read
  off both renders independently; the two agree with each other and with the
  KiCad symbol.
- Dimensions: page 32 rendered at 150 dpi (whole page) and at 300 dpi
  (cropped table, upper and lower halves); every MIN/NOM/MAX cell read from
  the render; all 16 rows then re-verified by decoding the font glyph map and
  comparing against the render (see the quirk section).
- Quotes: pins quote Table 3-1 rows on page 15 (clean ASCII text layer);
  dimensions quote the byte-exact page-32 rows. `validate` confirms every
  quote is on its cited page.
- `validate` (with `--datasheet`): **passed**, `failed: []`; 16 warnings, all
  `status.inferred` (10 dimensions + 6 pins: DOUT, CLK, DGND, AGND, VREF,
  VDD) — the intended flags for human review.
- `build`: symbol `MCP3008-I_SL.kicad_sym` generated with all 16 pins;
  footprint **skipped** with `footprint.skipped` ("land pattern is
  incomplete; add land_pad_length, land_pad_width, land_span") — correct,
  since the datasheet has no 16-lead land pattern and none was invented.

## MPN

Page 37 ("PRODUCT IDENTIFICATION SYSTEM") defines the orderable grammar and
prints, for the SOIC package of this device: "MCP3008-I/SL: Industrial
Temperature, SOIC package" (example b). The package-marking example on page 26
prints the same number as the mark would read: "MCP3008 / I/SL e3" (marking
drops the hyphen and appends the Pb-free designator). `mpn` is recorded as
**MCP3008-I/SL** — the orderable as printed, package suffix included. The
Device list also prints MCP3008T (tape-and-reel); the non-T industrial SOIC
orderable is the one the identification system spells out as an example, and
the reference's tape-and-reel rule points the same way. The bare "MCP3008"
(the description-page form) appears only as the device name, not as an
orderable, so it is not used.

`datasheet.revision` is **DS21295D** — the literature number with revision
letter as printed in every page footer ("DS21295D-page N"); this datasheet
prints no separate revision-history block. `datasheet.url` is the canonical
document URL, which matches the Datasheet property the KiCad symbol carries
for this part.

## Correction — 2026-10-24 (round-6 adjudication, [GOLD])

**What changed:** `land_pad_length` {max: 1.5}, `land_pad_width` {max: 0.6}, `land_span`
{nom: 5.4} added — status `inferred`, page 33, quote `MCP3004/3008`. The original gold
recorded no `land_*` and claimed above that the datasheet's only land pattern belongs to the
8-lead SN package.

**Why:** page 33 carries "16-Lead Plastic Small Outline (SL) – Narrow, 3.90 mm Body [SOIC]",
drawing **C04-2108A** — a RECOMMENDED LAND PATTERN with 16 pads for exactly the package the
recorded `mpn` `MCP3008-I/SL` orders (page 37, Product Identification System example b:
SL = "Plastic SOIC, 14-lead, 16-lead"). Verified at 300 dpi: Contact Pad Length
**Y = 1.50 MAX**, Contact Pad Width **X = 0.60 MAX**, Contact Pad Spacing **C = 5.40 NOM**;
C's extension lines are the dashed pad-row centre-lines, corroborated by C = G + Y =
3.90 + 1.50. The page-33 table is pure vector with no text layer, so the quote is the page's
only ASCII row — it pins the page; the values are `inferred` reads from the render, exactly
like the page-32 dimensions. Found by the round-6 adjudicator on a full independent read;
run1 had recorded these three values first and was scored wrong against the original gold.
