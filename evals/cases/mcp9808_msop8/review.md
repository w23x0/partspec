# Review — mcp9808_msop8

Case gold for the Microchip MCP9808, MS package (8-lead MSOP), datasheet DS25095A
(sha256 `9578bb72…`, 52 PDF pages). Everything in this gold was taken from that file only;
the DFN-8 half of the document (outline page 38, land pattern page 39, EP pin 9 in Table 3-1)
was excluded — it is a different package.

The controlling quirk of this datasheet: the package-drawing pages (38–41) are set in a
custom `Symbol` CID font whose glyph bytes are ASCII shifted by −0x1D (`8QLWV` → "Units",
`6%&` → "BSC") and whose digits and spaces became control bytes (`\x13` = "0", `\x11` = ".",
`\x03` = space). No ASCII digit on those pages is a real value — every one of them decodes to
a letter of a garbled word. So the digit values of the outline and land tables cannot be
quoted; they were read from 150/300 dpi renders (`pdftoppm`) and cross-checked against a
Python decode of the byte-shifted text layer. The two methods agreed on every row.

## Status calls under the skill's definitions

- All 8 pins: number and name read from Table 3-1 (page 11, real text) and the pairing
  verified on the rendered page-1 figure → `extracted` for the five pins whose electrical
  type the sheet states in prose ("SDA is a bidirectional input/output pin", "The SCL is a
  clock input pin", "These pins are device address input pins").
  Alert / GND / VDD types go through the skill's open-drain / ground / supply mapping rows →
  `inferred` (the sheet prints no I/O column).
- All 13 dimensions: `inferred`. The skill requires an `extracted` dimension's quote to carry
  min/nom/max as readable numbers; on these pages the text layer physically carries the
  digits only as control bytes, so no quote can satisfy that bar even though every value was
  visually confirmed on the renders. They are marked interpretations, recorded with the
  byte-exact `pdftotext -layout` row as the page-local quote (for page 41, whose drawing text
  is not extractable at all, the page footer row is the only byte-exact anchor). The quotes
  pass `check_quotes`; the checker does not test inferred values against them.

## KiCad disagreements

Cross-checked against `/usr/share/kicad/symbols/Sensor_Temperature.kicad_sym` (the part is
`MCP9808_MSOP`, which extends `MCP9804_MSOP` — there is no bare `MCP9808` symbol in the
library) and
`/usr/share/kicad/footprints/Package_SO.pretty/MSOP-8_3x3mm_P0.65mm.kicad_mod`.

| Where | Datasheet (this gold) | KiCad | Decision |
|---|---|---|---|
| Pin names 1–8 | SDA, SCL, Alert, GND, A2, A1, A0, VDD | same 1–8, except pin 8 is styled `V_{DD}` | Keep datasheet `VDD` (Table 3-1 and the pinout figure print `VDD`); styling is a symbol cosmetic. |
| Pin 3 type | `open_collector` (inferred) | `output` | Keep `open_collector`: §3.3 says "the temperature Alert output pin is an open-drain output" and the skill maps open-drain to `open_collector`. KiCad's `output` is weaker than the sheet's own words. |
| Pins 1,2,4–8 types | bidirectional / input / power_in ×2 / input ×3 | identical | Agree. |
| `land_span` | 4.40 (C, nom) | pad rows at ±2.1125 → 4.225 | Keep 4.40: the gold records Microchip's own land pattern (drawing C04-2111A), not KiCad's. |
| `land_pad_length` | 1.45 max (Y1) | pad 1.625 long | Keep 1.45 (same reason). |
| `land_pad_width` | 0.45 max (X1) | pad 0.4 wide | Keep 0.45 (same reason). |
| `pitch` | 0.65 BSC | 0.65 pad pitch | Agree. |
| `body_length`/`body_width` | 3.00 / 3.00 BSC (D / E1) | fab outline 3.0 × 3.0 | Agree. |
| `overall_width` (E = 4.90 tip-to-tip), `height`, `body_thickness`, `standoff`, lead dims | recorded | not modelled in the footprint (courtyard 3.18 is not a lead-tip span; heights live in the 3D model) | Nothing to disagree with; recorded from the datasheet alone. |
| Exposed pad | none (Table 3-1 row 9 prints `—` under MSOP; the MSOP diagram and drawing C04-111B have no pad) | footprint has 8 pads, no EP; `MCP9808_DFN` is the EP variant | Agree. |

Note, not a pin/dimension disagreement: the KiCad symbol's Datasheet property URL points at
DS20005095B (a later Microchip revision); this case pins DS25095A, whose sha256 is in the gold.

## Values that had to be interpreted

- Every dimension value (all 13): read from renders because the text layer carries no digits
  (see above); each is `inferred`.
- Callout-to-name mapping, read off the rendered page 40 by following extension lines:
  D (body edges) → `body_length` 3.00 BSC; E1 (moulded body across) → `body_width` 3.00 BSC;
  E (lead tips across) → `overall_width` 4.90 BSC; A → `height` max 1.10;
  A2 → `body_thickness` 0.75/0.85/0.95; A1 (body underside to seating plane) → `standoff`
  0.00–0.15; b → `lead_width` 0.22–0.40; c → `lead_thickness` 0.08–0.23;
  L (flat foot, bend to tip) → `lead_length` 0.40/0.60/0.80; e → `pitch` 0.65 BSC.
  Note 2 on the drawing ("Dimensions D and E1 do not include mold flash or protrusions")
  confirms D/E1 are body dimensions.
- Land pattern (page 41, drawing C04-2111A): C is drawn between the dashed row centre-lines →
  `land_span` 4.40 nom; X1 → `land_pad_width` 0.45 max; Y1 → `land_pad_length` 1.45 max.
  Internal consistency: C = Y1 + G1 (1.45 + 2.95 = 4.40) and Z = C + Y1 (4.40 + 1.45 = 5.85).
- Pin 8 name recorded as `VDD` although the electrical-spec tables print `VDD` with subscripts
  in places; Table 3-1 prints plain `VDD`.

## Deliberately left out

- `L1` "Footprint" 0.95 REF on page 40: the body-face-to-tip lead span, which the skill
  explicitly excludes (`lead_length` is the foot only), and a REF dimension besides.
- Foot angle φ 0°–8°: no dimension name exists for an angle.
- Land pattern page 41: Z (Overall Width 5.85 max), G1 (2.95 min), GX (0.20 min) — no `land_*`
  name models them (G1/GX are pad gaps, not pad metal; the skill takes the three pad
  dimensions as one set and nothing else). `land_ep_size` does not exist (no EP).
- `overall_length`: the drawing's only along-rows dimension is D, which measures the moulded
  body; no tip-to-tip-along-rows callout exists, so per the skill it is left out rather than
  naming D twice.
- DFN-8 entirely: outline page 38 (drawing C04-123C), land pattern page 39 (C04-2123B),
  EP pin 9, exposed-pad D2/E2/A3 values. Different package.
- `nom` for A1, b, c (the drawing prints `–` there); `min`/`nom` for A (both `–`).
- The DFN "8-Pin 2x3 DFN" column of Table 3-1 and the page-1 DFN diagram: only the MSOP column
  values were used (they coincide for pins 1–8; the quote rows carry both columns).

## Contradictions inside the datasheet

None found that touch pins or dimensions. Checked specifically: Table 3-1 (page 11) against
the page-1 Package Types figure (same 8 pairings; EP marked DFN-only by the `*` note);
drawing C04-111B's table against its own callouts (consistent); "8-Lead MSOP (3x3 mm)" on
page 37 against D/E1 = 3.00 BSC (consistent); thermal data (`8L-MSOP` θJA 211 °C/W, page 21)
and package marking (page 37) do not overlap the extracted fields. The closest thing to a
trap is the two-package layout of pages 1, 11, 38–41 — documented above rather than a
contradiction.

## Coverage of the verification

- `sha256sum` recorded; PDF index equals the printed page number for all pages used (1–42).
- Page 1 rendered at 150 dpi and the 8-Pin MSOP diagram again at 300 dpi: pin pairing
  SDA 1 / SCL 2 / Alert 3 / GND 4 / A2 5 / A1 6 / A0 7 / VDD 8 verified visually.
- Page 11 Table 3-1 read from the text layer (real text); all 8 rows quoted byte-exactly.
- Page 40 rendered at 150 dpi (whole page) and 300 dpi (drawing area and every table row):
  all ten outline values and every callout's extension lines verified visually; independently
  cross-checked against the +0x1D decode of the garbled text layer — agreement on all rows.
- Page 41 rendered at 150 dpi and its table and figure again at 300 dpi: all land values and
  the C centre-line arrows verified visually; confirmed no exposed pad and a pin-1 dot.
- Pages 38 and 39 rendered: identified as the DFN package (C04-123C / C04-2123B) and excluded;
  their values (e.g. e 0.50, A 0.80–1.00) appear nowhere in this gold.
- Text search for land-pattern/footprint sections found none outside pages 39/41 (the two
  "RECOMMENDED LAND PATTERN" sheets); page 39 is the DFN one, page 41 the MSOP one.
- KiCad symbol and footprint cross-checked as tabulated above.

## mpn

The datasheet prints one orderable for this package, in the Product Identification System
(page 49): "b) MCP9808-E/MS: Extended Temperature 8LD MSOP package." — so the gold records
`MCP9808-E/MS`, suffix and all. `MCP9808T-E/MS` (example d) is the same part with the
tape-and-reel designator `T` ("MCP9808T: Digital Temperature Sensor (Tape and Reel)"); per the
skill the tape-and-reel form is not the recorded mpn. No other page prints an orderable:
the cover lists only packages ("2x3 DFN-8, MSOP-8") and page 37 shows the marking code
("9808E" example), so `MCP9808-E/MS` is the exact printed string, not a package-only form.

## Validate / build outcome

- `kicad-partspec validate spec.gold.json --datasheet ~/datasheets/mcp9808_msop8.pdf`:
  **passed, `failed` empty.** All quotes (real-text pin rows, control-byte garbled rows on
  page 40, footer row on page 41) matched their cited pages. 16 warnings, all
  `status.inferred` — the honest marks described above.
- `kicad-partspec build` (0 failures): symbol `MCP9808-E_MS.kicad_sym` generated, and a
  footprint **generates** — `MSOP-8_3.0x3.0mm_P0.65mm.kicad_mod`, pads 1.45 × 0.45 at span
  ±2.2 (pitch 0.65): the datasheet's own land pattern, not a `footprint.skipped` case, because
  MSOP's recommended land pattern exists in the datasheet (page 41). No numbers were invented.
