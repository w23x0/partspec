# kicad-partspec

**Pre-alpha.** Tools for turning datasheet evidence into traceable KiCad parts and checking explicit circuit requirements.

The project supports the work around model extraction: finding drawings that text search misses, reading several pages
at once, preserving the connection between each value and its source, and handing off unresolved work clearly. It works
with any model or a human author. It does not call a model API.

The core remains **PDF → PartSpec JSON → KiCad symbol and footprint**. The `project` operation brings parts, existing
circuits, review records and generated libraries into one report and handoff. Its circuit checks use physical pin numbers
and explicit requirements. PDF checking and KiCad loading are opt-in; no model or simulator runs automatically.

## What you can do

| Need | Operation | Result |
|---|---|---|
| Work on a complete parts-and-circuits project | `project` | One manifest, searchable report, prioritized actions, evidence copies, BOM, library tables and changes since a baseline |
| Find pin tables, drawings and pages with broken text | `prepare` | Every page indexed, selected previews, labeled contact sheets, HTML gallery |
| Read several drawings without one tool call per page | `read-pages` | Full page text, images and optional image crops |
| See what is established and record review decisions | `review` | Fields and quotes by page, attributed decisions, stale-review detection, remaining work |
| Process a collection of parts | `batch` | Per-part results and artifacts, failed-job list, no overwriting earlier batches |
| Catch incorrect wiring and component choices | `circuit-check` | Physical-pin checks, output conflicts, net constraints, capacitor totals with tolerance, voltage ratings |
| Reuse wiring from an existing KiCad design | `circuit-import` | Bind an exported XML netlist to PartSpec files, preserve DNP and no-connect markers |
| Generate or check library files | `validate`, `build`, `verify` | Existing PartSpec, source, symbol, footprint and optional KiCad load checks |

Preview selection is a navigation aid. A page with no searchable text stays in the inventory. Quote matching proves that
text occurs on a page; the value's association with a pin, package or dimension still needs visual review. Review reports
keep those states separate. Circuit checks cover the requirements supplied; they do not establish electrical performance.

## Install the working version

Python 3.10 or later. From this checkout:

```bash
pip install -e ".[mcp,pdf]"
```

The base CLI has no Python runtime dependencies. The `mcp` extra installs the MCP server; `pdf` installs Pillow for images
and contact sheets. Install Poppler (`pdftotext` and `pdftoppm`; on Debian/Ubuntu, `apt install poppler-utils`) for PDF
operations. KiCad 9 or later is optional for library load checks. New commands described here are checkout features;
an older package from PyPI may not contain them.

The wheel contains the Python tools. The extraction skill and plugin manifests live in the repository. For development,
configure your MCP client to run the installed `kicad-partspec-mcp` command and set `PARTSPEC_WORKSPACE` to your project
directory. The Claude plugin's `.mcp.json` uses `uv run --project ${CLAUDE_PLUGIN_ROOT}` with the `mcp` and `pdf` extras,
so it runs the plugin's own checkout and needs `uv` on PATH. Other MCP clients can use the installed command directly.

## Start with one project manifest

Use [examples/project.json](https://github.com/w23x0/kicad-partspec/blob/main/examples/project.json) to see how part files,
review evidence and circuit inputs fit together. From the repository root:

```bash
kicad-partspec project examples/project.json --workspace . --out work/review-1 --concise
```

Open `work/review-1/index.html`. It lists each task, its actual check states, failures and remaining review work. The bundle
contains the full `project.json`, individual reports, copied evidence images/text when supplied, and BOM JSON/CSV with DNP
preserved. An unreadable or failed task stays visible while independent tasks continue.

This invented example deliberately includes an unpopulated capacitor and an incomplete footprint source. It should report
the unmet capacitance requirement and outstanding part work. It is a format example, not a manufactured or validated design.

To generate the requested libraries and compare with an earlier result:

```bash
kicad-partspec project examples/project.json --workspace . --operation build --out work/build-1 --concise
kicad-partspec project examples/project.json --workspace . --out work/review-2 \
  --baseline work/review-1/project.json --concise
```

Successful library generation adds `sym-lib-table` and, when footprints exist, `fp-lib-table`, using paths relative to the
bundle. Earlier outputs are preserved. Baseline comparison names changed input files and new/resolved failures; changing
the requested check scope is shown separately. A disabled check is never reported as a repaired failure.

`project` defaults to reading existing JSON, XML and evidence assets. `--check-pdf` explicitly enables source checks for
parts with a PDF path; `--check-kicad` explicitly enables loading during `--operation build`. The operation does not extract
PartSpecs, render new pages or contact a model. Use the page tools below while preparing inputs.

The [project guide](https://github.com/w23x0/kicad-partspec/blob/main/skills/partspec/project.md) describes the manifest,
output layout and how to use the handoff. The individual tools remain useful for focused work on one part or circuit.

## Prepare the evidence and PartSpec inputs

```bash
kicad-partspec prepare datasheets/part.pdf --out work/evidence --term PART-NUMBER --term DRAWING-CODE
kicad-partspec read-pages datasheets/part.pdf --pages 3,18-20 --out work/drawings --dpi 220
```

Open `work/evidence/index.html` and the contact sheets, inspect the selected drawings, and fill a PartSpec using the
[extraction reference](https://github.com/w23x0/kicad-partspec/blob/main/skills/partspec/reference.md).
The tools do not extract or infer values automatically. PDF page indexes start at 1; they are not printed page labels.
`prepare --preview-limit 0` creates a text inventory without Pillow or `pdftoppm`.

```bash
kicad-partspec review parts/part.json --evidence work/evidence/manifest.json --out work/review
kicad-partspec validate parts/part.json --datasheet datasheets/part.pdf
kicad-partspec build parts/part.json --out work/library --no-kicad
```

`review` checks the PartSpec and evidence identity. Supplying `--datasheet` additionally runs PDF hash and quote checks;
without it, source text is reported as `not_run`. It produces `handoff.json`, `REVIEW.md` and `review-input.json`.
Record decisions in the template with the reviewer, human/model kind and a note, then pass it as `--decisions` to a new
review. Decisions are bound to the PartSpec content and review scope: changed inputs invalidate previous decisions.
Rejected items remain failures; source checking and electrical validation are not implied by a recorded visual review.
Review and page-reading output directories must be new. Existing standalone `build` behavior is retained: it can
overwrite generated files and attempts KiCad loading unless `--no-kicad` is set.

Footprints use the datasheet's example land pattern, not guessed library names or package-outline dimensions.
Supported families include symmetric dual-row SOIC/SOP/SSOP/TSSOP/MSOP/VSSOP/SOT-23/TSOT-23 and quad
QFN/VQFN/WQFN/UQFN/QFP/TQFP/LQFP packages. Missing land patterns and unsupported layouts, such as unequal-row SOT-23-5,
produce a symbol and an explicit `footprint.skipped` warning. Symbols target the KiCad 9 file format (20241209).

## Batch work and circuit requirements

```bash
kicad-partspec batch examples/batch.json --workspace . --operation review --out work/batch-review
kicad-partspec batch examples/batch.json --workspace . --operation build --out work/batch-build
kicad-partspec circuit-check examples/circuit.json
kicad-partspec circuit-import examples/circuit-import.json --workspace . --out work/imported-circuit
```

The checked-in examples use an **invented** part and passive values to explain the formats. They are not a reference
design for fabrication. Batch jobs resolve paths inside the workspace, preserve individual errors, and publish successful
part folders separately. KiCad loading in a batch requires `--check-kicad`; PDF checks run only for jobs carrying a
`datasheet_path`.

The circuit format accepts inline PartSpecs and generic two-terminal resistors/capacitors. Checks include unknown and
reused pins, declared no-connect pins, undocumented unused pins, and multiple driven outputs. Requirements support
`same_net`, `separate_nets`, `capacitance_between`, and `voltage_rating`. Capacitance defaults to the lower tolerance bound
and counts only capacitors directly across the named nets. DC-bias derating, temperature, transient behavior and layout
effects are outside this arithmetic check.

`circuit-import` reads an existing **KiCad XML netlist** without starting KiCad. Bind each real component reference to a
PartSpec file or an explicit resistor/capacitor kind. It reads complete value labels such as `4k7`, `10k` and `22uF`, keeps
physical pin numbers and footprint names, and imports DNP/no-connect markers. Ratings and tolerances remain explicit
inputs. Unbound components and expected-footprint mismatches fail instead of disappearing from the circuit.

The import example deliberately leaves C2 unpopulated. C1's 22 µF ±20% contributes only 17.6 µF, so the 22 µF requirement
is expected to fail. This demonstrates why DNP parts must not inflate the checked capacitance. Import output includes
the circuit, original netlist, binding manifest and findings; inspect `passed` before relying on the supplied constraints.

See the [workflow and format guide](https://github.com/w23x0/kicad-partspec/blob/main/skills/partspec/workflows.md) for
schemas, output interpretation and MCP arguments. MCP exposes `partspec_project` plus nine focused tools:
`partspec_prepare`, `partspec_read_pages`, `partspec_review`, `partspec_batch`, `partspec_circuit_import`,
`partspec_circuit_check`, `partspec_validate`, `partspec_build`, `partspec_verify`.

## Development and evidence

Development follows concrete user needs with focused local checks. Model experiments, PDF corpus runs, KiCad round trips,
full audits and unattended loops are separate opt-in work. Report exactly what was exercised and what was not.
The [agent workflow](https://github.com/w23x0/kicad-partspec/blob/main/AGENTS.md) retains extraction conformance and gold
arbitration safeguards; the audit board measures that existing subsystem, not overall product progress.

Historical extraction measurements and their limitations are in
[evals/README.md](https://github.com/w23x0/kicad-partspec/blob/main/evals/README.md). Their answer keys were written and
checked by models and have not all been reviewed by a human. The
[electronics research note](https://github.com/w23x0/kicad-partspec/blob/main/research/fable-5.2-electronics-2026-11-14.md)
motivates the workflow changes; it is not a model benchmark performed by this project.

## History and license

This repository replaces `codex-kicad-mcp`; its code remains on the `legacy` branch and tags `v0.2.0`/`v0.2.1`. MIT license.
