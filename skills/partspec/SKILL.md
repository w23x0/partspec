---
name: partspec
description: Prepare datasheet evidence, extract traceable KiCad parts, and deliver project reports with circuit requirements, review records, BOM and libraries. Use for datasheet-based parts or projects that combine parts and explicit reference-circuit netlists.
---

# PartSpec: evidence, KiCad parts and circuit requirements

You read the datasheet and fill a **PartSpec** (a JSON file). Deterministic code turns it into KiCad files and verifies them.
Extract facts accurately. Every value carries the datasheet page and a **verbatim quote**, so a human can
audit each one. Never fill a value from memory or from other parts of the same family: if the datasheet in front of you does
not state it, leave it out and say so.

For work spanning parts and circuits, start with `partspec_project` and read [project.md](project.md): one manifest produces
the combined report, evidence handoff, BOM, library tables and comparison with an earlier result. Use the focused tools to
prepare or correct its inputs; a project pass does not replace source/visual review.

Use `partspec_prepare`, `partspec_read_pages`, `partspec_review`, `partspec_batch`, `partspec_circuit_import` and `partspec_circuit_check` alongside
`partspec_validate`, `partspec_build` and `partspec_verify`. The CLI exposes the same operations. Read
[reference.md](reference.md) for the authoritative extraction rules; [example.json](example.json) is an invented part.
Read [workflows.md](workflows.md) for batch manifests, circuit requirements or evidence output details.
Follow the user's requested verification scope; do not start model experiments, hardware tests or an end-to-end run merely
because these tools are available. A check not executed remains `not_run`.

## Workflow

1. **Find the pages.** Use `partspec_prepare` with the part number and drawing codes in `terms`. It indexes every page and
   returns a gallery and labeled contact sheets. Page numbers are PDF page indexes, starting at 1 (not printed labels).
   You need: the pin table or pinout, the package outline drawing (with its dimension table), and the example land pattern
   ("board layout" / "recommended footprint"). The drawings are usually near the end, far from the pin table: search for the
   package's drawing code (for example a name like `D0008A` or `RGT0016C`) or for "PACKAGE OUTLINE". If the PDF covers several
   packages or several parts, use only the one you were asked for. Inspect `pages_needing_visual_read` even without keyword
   matches; selected previews do not prove there is no relevant drawing on an unrendered page.
2. **Look at the drawings.** Text extraction keeps numbers but loses which dimension they belong to, and pinout figures put
   pin numbers and names in different places. Use `partspec_read_pages` for several pages at once, then open the returned
   images with the client's image viewer. Higher DPI and normalized crops help with small labels; text still covers the
   full page. If PDF tools are unavailable, report what cannot be read. Do not silently substitute OCR text for source quotes.
3. **Keep document identity.** The SHA-256 returned by `prepare` goes in `datasheet.sha256`; pass it as `expected_sha256`
   when reading pages. A vendor rebuild is a different file; preserve any explicit rebuild finding.
4. **Write the PartSpec** as JSON, following [reference.md](reference.md).
5. **Review and validate within scope.** `partspec_review` groups fields by source page and exposes missing evidence,
   inferred fields and footprint blockers. To check PDF text, supply `datasheet_path`, or use
   `partspec_validate` with it (CLI: `kicad-partspec validate SPEC.json --datasheet FILE.pdf`).
   Every entry in `failed` says what to change. A `prov.quote_not_found` means your quote is not on that page as printed.
6. **Build when requested**: `partspec_build` (CLI: `kicad-partspec build SPEC.json --out DIR`; add `--concise` to see failures in full and warnings
   only counted by kind, which keeps the one important warning from being buried). Fix any failure and rebuild. A `footprint.skipped`
   warning means the datasheet's land pattern is missing, incomplete or unsupported; report it, do not invent the numbers.
   Use `check_kicad=false` / `--no-kicad` when loading is outside scope. For multiple parts, use a batch with a new output
   directory; each part gets separate findings and a handoff, and KiCad loading is opt-in.
7. **Hand over for review.** Save the `partspec_review` packet or the batch handoff. Tell the user which pins and dimensions are `inferred`, anything you left out and why, and any place
   where two parts of the datasheet disagree. Do not mark anything `confirmed`; only a human does that.
   The output includes `review-input.json` for attributed decisions. Record only reviews actually performed, using the
   correct human/model kind; never label your own review as human. Pass completed entries as `decisions_path` on a later
   review. If the PartSpec or scope changes, review the new template rather than copying its hash onto old decisions.

For circuit work, record nets using physical pin numbers and write the intended constraints explicitly before running
`partspec_circuit_check`. It can check connection requirements, parallel capacitor totals and component voltage ratings.
For an existing KiCad XML export, use `partspec_circuit_import` to bind each reference to its PartSpec file or explicit
passive kind. Check part/value and footprint mismatches, DNP flags and tolerances before interpreting the requirements.
It does not derive a complete circuit from a drawing or establish analog performance. See [workflows.md](workflows.md).

## Quotes

- Build every quote from `pdftotext -layout` output. Plain `pdftotext` orders the text differently and its quotes will not match.
- Copy text exactly as printed on the cited page. Whitespace and line breaks do not matter; characters do (keep en dashes such as `IN1–`).
- Quote enough to contain the value and its label, no more: a table row (`5 FB I`), or the tokens beside a dimension.
- The quote must be on the page you cite. A pinout page can repeat the same labels for two packages (say a TQFP view and a
  QFN view); use the labels of the package you were asked for.
- Numbers in a figure are interleaved with other labels in the text layer. Two numbers that belong together may be printed as
  `1.0 C 0.8`, not `1.0 0.8`, and a value and its bracketed millimetres are often on different lines. Two ways out: quote one
  token (`.189-.197`, even if the value you record is the millimetre one), or use the hint `kicad-partspec validate --datasheet`
  gives on a failed quote, which is the page's own token order.
- In a pinout figure the number and the name may sit apart (rotated labels), so a quote can only carry the name. Check the
  pairing on the rendered image; that is the reason step 2 exists.
- When the pinout figure and a pin table disagree on a name (RP2040: the figure says `SWDIO`, the table says `SWD`), use the
  figure's name — that is what board designers read — put nothing in `alt_names` for it, and list the disagreement in the
  hand-over.
- The same goes for a name that belongs to a sibling part. When one datasheet documents several parts (MCP23008 and
  MCP23S08), a pin cell that prints two names (`SCL/SCK`, `A2/SO`, `NC/CS`) gives one name for each part, not two functions
  of yours: take the one printed for the part you were asked for, leave `alt_names` empty, and list the pairing in the
  hand-over.

## Rules that prevent the usual mistakes

- One pin entry per **physical pin**. A row such as `1,2,3  SW` is three pins with the same name.
- `package.family` is the family the datasheet names: TI's `DDC (SOT-23, 6)` is `SOT-23`, not `SOP`. Never rename it to get a
  footprint out of the build — an unsupported family gives a `footprint.skipped` warning, which is the honest outcome, and
  you report it in the hand-over.
- A **no-connect** pin still gets an entry (type `no_connect`).
- An exposed/thermal pad gets `exposed_pad: true` and one pin entry numbered `pin_count + 1`, marked `inferred` if the datasheet gives it no number.
- Dimensions are millimetres. If the drawing prints inches with millimetres in brackets, use the bracketed millimetres.
- Leave a dimension out when the drawing does not make clear what it is. A wrong number is worse than a missing one.
- `land_*` dimensions come only from the datasheet's example land pattern, never from the package outline.
- `inferred` is honest, not a failure: use it whenever you derived a value instead of reading it.
