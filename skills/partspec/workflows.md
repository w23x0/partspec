# Workflow interfaces

These are tool input/output formats. PartSpec extraction semantics remain in [reference.md](reference.md).
For a combined parts-and-circuits operation, use [the project workflow](project.md). The commands below are its focused
input-preparation and inspection tools.

## Evidence preparation and page reading

`partspec_prepare(datasheet_path, out_dir, terms?, preview_limit=24)` corresponds to CLI `prepare`.
It runs `pdftotext -layout` on the PDF, saves every page's text, and selects up to 32 previews across pinout, outline,
land-pattern, ordering, search-term, broken-text and tail-page groups. Selection is heuristic. Sparse means fewer than
40 alphanumeric characters; broken means control/replacement characters were found. Searchable text may still be wrong.
These labels prioritize inspection; they do not classify a page as irrelevant.

`manifest.json` uses `schema: "partspec.evidence/v1"` and contains `pdf`, `sha256`, `page_count`, `terms`, `pages` and
`contact_sheets`. Each page has its 1-based `page`, `text_quality`, `topics`, `term_matches`, `text_file` and optional
`preview`. Relative file paths start at the manifest directory. `index.html` shows all pages, including unrendered pages.
Every output directory must be new; a failed preparation does not publish a partial packet. `preview_limit=0` skips images.

`partspec_read_pages(datasheet_path, pages, out_dir, dpi=180, crop?, expected_sha256?)` accepts a page expression such as
`"1,7-9,12"`. At most 32 pages, DPI 72..600. A crop is `[left, top, right, bottom]` in normalized page coordinates, e.g.
`[0.1, 0.2, 0.9, 0.8]`. It affects only the image. Text always covers the whole page, is capped at 8000 characters per page
in the response with a truncation flag, and is saved in full to disk. Responses give image/text paths and labeled contact
sheets; the client must open images to inspect them. `expected_sha256` rejects a PDF different from the indexed bytes.

## Review and handoff

`partspec_review(spec_path? | spec?, datasheet_path?, evidence_path?, decisions_path?, out_dir?)` checks the PartSpec and returns a
`partspec.handoff/v1` report. Pass exactly one of the PartSpec inputs. `evidence_path` points to the preparation manifest;
its SHA-256 must match the PartSpec. The report groups values and quotes by PDF page, carries inferred fields and
footprint blockers, and produces actionable work items. With `out_dir`, it saves `handoff.json`, `REVIEW.md` and `review-input.json`.

`passed` only means no executed check failed. Read `checks` and `actions` as well:

| State | Meaning |
|---|---|
| `input_checks` | Structure, extraction checks and supplied evidence identity |
| `source_text: not_run` | No datasheet PDF supplied for quote checking |
| `source_text: blocked` | Malformed PartSpec prevented source checking |
| `source_text: passed_on_rebuilt_pdf` | Existing same-revision fallback was used; original PDF bytes did not match |
| `visual_binding: requires_review` | Pin pairing, dimension lines, package choice and copper/mask boundaries still need inspection |
| `visual_binding: recorded_human_review` / `recorded_model_review` / `recorded_mixed_review` | Every review target has an accepted, attributed record of the indicated kind |
| `visual_binding: rejected` | At least one supplied review record rejects a target; this is a failure |
| `kicad_load: not_run` | No KiCad load operation was performed |
| `electrical_function: not_run` | No electrical validation was performed |

A matching quote is not proof that the value belongs to the desired pin or dimension. Previewing a page does not mark it
reviewed. Sparse/broken pages with no citations appear in a separate inspection action so missing evidence stays visible.
Image paths point into the evidence packet; keep that packet with the handoff. Never turn OCR output into a fabricated
verbatim PDF text-layer quote. Missing source text remains unresolved under the existing extraction rules.

### Saving decisions and detecting stale reviews

The `review-input.json` template uses `schema: "partspec.review/v1"`, `spec_sha256`, `scope_sha256` and a `decisions` list.
Hashes cover canonical JSON content; whitespace and object-key order do not matter. The scope includes the part/package
binding, cited fields and uncited sparse/broken pages. Use the same evidence inventory when applying decisions.
Each entry has a `target`, `verdict`, `reviewer_kind`, `reviewer`, `reviewed_at` and `note`:

```json
{
  "target": "pins[0]",
  "verdict": "accepted",
  "reviewer_kind": "model",
  "reviewer": "the actual model/reviewer identifier",
  "reviewed_at": "2026-11-15T12:00:00+08:00",
  "note": "Record what was inspected and why the pairing is supported."
}
```

The snippet illustrates one entry, not a completed review. Fill in the actual observation after inspecting the source.
Allowed verdicts are `pending`, `accepted`, `rejected` and `needs_info`; pending entries may leave attribution blank.
Other verdicts require a reviewer kind (`human` or `model`), identifier, an ISO 8601 timestamp with timezone, and non-empty
note. The timestamp in the snippet is illustrative; record when the actual review happened. Missing entries remain pending.
Unknown/duplicate targets or malformed decisions invalidate the file; rejected entries produce findings and block batch
generation. `needs_info` stays in the review queue. Reports display notes, counts and attribution without authenticating
the claimed reviewer identity or changing `inferred` to `confirmed` in the PartSpec.

```bash
kicad-partspec review parts/part.json --evidence work/evidence/manifest.json --out work/review-1
# Inspect the report and source; fill review-1/review-input.json with actual decisions.
kicad-partspec review parts/part.json --evidence work/evidence/manifest.json \
  --decisions work/review-1/review-input.json --out work/review-2
```

Changing the PartSpec or review scope produces `review.stale_decisions` and retains the work as pending. Start from the
new template and reconsider the affected evidence; do not replace hashes to make old decisions appear current. Recorded
acceptance never clears independent source/spec failures. A model's acceptance of inferred fields still leaves human
inference review visible. This mechanism records visual work; it runs no visual model or hardware checks itself.

## Batch manifest

`partspec_batch(manifest_path? | manifest?, operation="review", out_dir?, check_kicad=false)` accepts:

```json
{
  "schema": "partspec.batch/v1",
  "jobs": [
    {
      "id": "regulator",
      "spec_path": "parts/regulator.json",
      "datasheet_path": "datasheets/regulator.pdf",
      "evidence_path": "work/regulator-evidence/manifest.json",
      "decisions_path": "work/regulator-review/review-input.json"
    }
  ]
}
```

There must be 1..100 jobs with unique IDs, 1..80 characters using letters, digits, underscores or hyphens, starting with
a letter or digit. `datasheet_path`, `evidence_path` and `decisions_path` are optional. Supply a PDF only when source validation is wanted.
`operation` is `validate`, `review` or `build`. `validate` ignores evidence navigation and decisions; `review` and `build` check them.

CLI paths in jobs and `--out` resolve relative to `--workspace`, defaulting to the manifest's directory. The manifest
argument itself is read relative to the shell working directory. MCP resolves the manifest and all nested paths inside
`PARTSPEC_WORKSPACE`, including symlinks. For the repository example use `--workspace .` from the repository root.

`build` requires a new output directory. `validate` and `review` can return reports without writing files. With output,
each job gets `partspec.json` and `checks.json`; review/build also get `handoff.json`, `REVIEW.md` and `review-input.json`. Successful builds add
`library/` with a per-job library nickname. Generated files that fail checks are withheld, while findings are retained.
An unreadable job gets an error report and does not prevent later jobs. `batch.json` lists counts and failed job IDs.
No job is silently skipped or treated as successful after failure. Previously created directories are never overwritten.

KiCad loading requires `check_kicad=true` / `--check-kicad`. A missing KiCad installation produces a warning and
`kicad_load: not_run`; it does not imply a successful load. If a footprint cannot be generated, the symbol can still be
published with a `footprint.skipped` warning and an outstanding `resolve_footprint` action.

## Circuit input

`partspec_circuit_check(circuit_path? | circuit?)` and `kicad-partspec circuit-check PLAN.json` read
`schema: "partspec.circuit/v1"`. They run only deterministic in-memory checks. See
[the invented circuit example](../../examples/circuit.json) for a complete input.

| Field | Input |
|---|---|
| `parts` | Object mapping catalog keys to inline PartSpec objects; no PDF reading occurs |
| `components` | Non-empty list of unique references; a ref must not contain `.` |
| `nets` | Non-empty list of `{ "name": "VCC", "pins": ["U1.1", "C1.1"] }`; names unique |
| `unconnected` | Optional object mapping an intentionally unwired `ref.pin` to a non-empty reason |
| `requirements` | List of explicit requirements with unique `id` and supported `kind` |

Component kinds:

- `part`: `{ "ref": "U1", "kind": "part", "part": "catalog-key" }`. Pins and electrical types come from its PartSpec.
- `capacitor`: `{ "ref": "C1", "kind": "capacitor", "capacitance_f": 0.000022, "tolerance": 0.2, "rated_voltage_v": 16 }`.
- `resistor`: `{ "ref": "R1", "kind": "resistor", "resistance_ohm": 10000 }`.

Generic resistors and capacitors have passive pins `"1"` and `"2"`. Quantities are finite SI numbers, not strings such as
`"22uF"`. Capacitance and voltage rating must be positive; zero-ohm resistors are permitted. Tolerance is a fraction from
0 inclusive to 1 exclusive. Passive values are supplied design inputs, not claims of datasheet extraction or stock availability.
Every component also accepts `populated` (boolean, default true). Unpopulated capacitors contribute no capacitance and
unpopulated outputs do not drive nets; a voltage-rating requirement cannot be satisfied by an unpopulated component.
The pad-level connections are still checked. Population is assembly metadata, not a way to erase wiring findings.

Every terminal must belong to exactly one net or have an explicit unconnected reason. A PartSpec `no_connect` pin is
allowed to remain unwired without a reason, but must not be wired. Unknown terminals, duplicate wiring, invalid part
references and multiple `output`/`power_out` pins on a net fail. This is a conservative output-conflict check, not KiCad's
complete ERC matrix; power delivery, open-collector pull-ups and intentional multi-driver circuitry need further rules.

| Requirement kind | Additional fields | Check |
|---|---|---|
| `same_net` | `pins`: at least two distinct connected endpoints | All are on the same net |
| `separate_nets` | `pins`: at least two distinct connected endpoints | All are on pairwise different nets |
| `capacitance_between` | `nets`: two distinct names; `min_f`; optional `basis` | Sum capacitors directly across the pair |
| `voltage_rating` | `ref`, `min_v` | The component's supplied `rated_voltage_v` meets the minimum |

Capacitance `basis` defaults to `minimum`: every counted capacitor needs tolerance and contributes `nominal × (1 − tolerance)`.
Use `basis: "nominal"` explicitly to sum nameplate values. No series-equivalent capacitance, DC-bias/temperature derating,
ESR, placement or transient analysis is inferred. For example, two 22 µF ±20% capacitors contribute 35.2 µF on the minimum
basis; one contributes 17.6 µF and fails a 22 µF requirement. Missing required fields and unsupported requirement kinds
produce failures rather than disappearing from the result.

The report uses `partspec.circuit-report/v1` with per-requirement expected/actual values, findings and `coverage`.
Without requirements it warns that only connectivity was checked. Coverage distinguishes requirements requested and
evaluated; failed input can prevent evaluation. A passing report means the supplied constraints passed, not that the
requirements are complete or that the circuit is ready for manufacture. It produces no schematic drawing or routed PCB.

## Import an existing KiCad netlist

`partspec_circuit_import(manifest_path? | manifest?, out_dir?)` and CLI `circuit-import` accept
`schema: "partspec.circuit-import/v1"`. Use an existing KiCad XML export, not a `.kicad_sch`, legacy S-expression netlist,
board file or guessed list of signal names. The importer does not invoke KiCad to produce the export.

```json
{
  "schema": "partspec.circuit-import/v1",
  "netlist_path": "design/export.xml",
  "bindings": {
    "U1": {"spec_path": "parts/regulator.json", "expected_footprint": "Project:RegulatorPackage"},
    "C1": {"kind": "capacitor", "tolerance": 0.2, "rated_voltage_v": 16},
    "R1": {"kind": "resistor"}
  },
  "requirements": [
    {"id": "bulk", "kind": "capacitance_between", "nets": ["VOUT", "GND"], "min_f": 0.000022}
  ]
}
```

Bind every actual reference explicitly. `spec_path` reuses an existing PartSpec; its physical pins are checked against the
imported connections. Do not also set `kind` for that binding. Generic passives use `kind: "resistor"` or `"capacitor"`;
their exported labels can supply the SI value. Supported labels include `4k7`, `4.7kΩ`, `0R`, `10M`, `100nF`, `22uF`,
`2u2` and decimal/scientific values with the proper unit. `m` means milli and `M` means mega. A bare capacitor label such
as `22` is ambiguous and fails. Labels containing extra text such as `10k 1%` fail; provide `resistance_ohm` or
`capacitance_f` explicitly for those labels. Tolerance and voltage ratings are never guessed from labels.

Unknown components, unused bindings and `expected_footprint` mismatches are failures. A symbol's value differing from the
bound PartSpec MPN is surfaced as a warning with both values, since generic symbol values often omit ordering suffixes.
The importer preserves the original value and footprint in each component and records netlist, manifest and PartSpec
hashes. It does not claim compatibility from a familiar reference prefix, symbol name or footprint name.

KiCad no-connect pin markers on singleton nets become explicit unconnected reasons. A marker on a connected net fails.
Manifest `unconnected` can document an intentionally unwired exported singleton; it cannot suppress an existing multi-pin
connection. Other singleton nets remain visible with an isolated-pin warning. Requirements and unconnected reasons use
the circuit format above; their original fields are preserved.

Exported DNP properties mark a component `populated: false`. Bindings may explicitly set `populated` for an assembly
variant; a difference from the export produces `netlist.population_override`. Capacitance checks exclude unpopulated
capacitors even though their pads remain on the nets. See [the import manifest](../../examples/circuit-import.json) and
[invented netlist](../../examples/circuit.net): C2 is DNP, so the 22 µF minimum deliberately fails with C1's 17.6 µF lower bound.

Paths follow the same workspace convention as batch. XML is bounded to 16 MiB and custom DTD/entity declarations are
unsupported. Without output, the report includes the circuit inline. With a new output directory it saves `import.json`
and `bindings.json`, plus `circuit.json` and the original `netlist.xml` when conversion succeeds. Conversion can succeed
while circuit requirements fail; `circuit_emitted` and `passed` deliberately describe different outcomes. Invalid bindings
prevent emission of a partial circuit. No simulation, PDF quote checking or physical validation occurs.

## CLI results

Reports are JSON. Exit 0 means executed checks passed (warnings/actions may remain); 1 means a check or operation failed;
2 means command usage or JSON reading failed. Existing `validate`, `build` and `verify` accept `--concise`.
MCP failures carry actionable messages. PDF tools need Poppler; image output also needs the optional Pillow dependency.
JSON inputs reject duplicate keys, NaN/Infinity and numbers outside the finite range instead of silently selecting a
value or propagating invalid calculations. A JSON `null` PartSpec is a structural failure, not an unreadable-file sentinel.
