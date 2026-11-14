# Project handoff

Use `partspec_project` / CLI `project` when a task spans a part catalog, review records and circuits. This operation composes
the focused tools described in [workflows.md](workflows.md). Extraction rules remain in [reference.md](reference.md).
See [examples/project.json](../../examples/project.json) for a complete invented input.

## Manifest and scope

The project object has `schema: "partspec.project/v1"`, a non-empty `name`, and `parts` and/or `circuits` lists.
Each list supports up to 100 jobs with unique IDs, using 1..80 letters, digits, underscores or hyphens and starting with a
letter or digit. Unknown fields are rejected so a misspelled input does not silently disappear.

| Part job field | Meaning |
|---|---|
| `id` | Stable catalog name and generated library nickname |
| `spec_path` | Required PartSpec JSON |
| `evidence_path` | Optional manifest from `prepare`; referenced image/text assets are copied into the bundle |
| `decisions_path` | Optional attributed review records for the matching PartSpec and review scope |
| `datasheet_path` | Optional source PDF; read for source checks only when `check_pdf` is enabled |

Each circuit job has `id` and exactly one of `circuit_path` (a `partspec.circuit/v1` document) or `import_path`
(a `partspec.circuit-import/v1` manifest binding an existing KiCad XML export). Import bindings reference PartSpec paths;
reuse the same files listed in the part catalog. Catalog matching uses exact canonical PartSpec content, not just MPNs.
This avoids treating two packages or revisions of the same part as interchangeable.

MCP arguments:

```text
partspec_project(
  out_dir,
  manifest_path OR manifest,
  operation="review",
  check_pdf=false,
  check_kicad=false,
  baseline_path?,
  response_format="concise"
)
```

CLI equivalents:

```bash
kicad-partspec project PROJECT.json --workspace PROJECT_ROOT --out work/review-1 --concise
kicad-partspec project PROJECT.json --workspace PROJECT_ROOT --out work/build-1 --operation build --concise
```

Job paths, nested import paths, output and baseline resolve within the explicit workspace, including symlink resolution.
The CLI defaults the workspace to the project manifest's directory; MCP uses `PARTSPEC_WORKSPACE`. The CLI manifest
argument itself follows the shell working directory. Output must be a new directory.

The default operation reviews existing PartSpecs and checks existing circuits. It copies supplied evidence assets without
rendering or inspecting images. `build` additionally generates library files and checks them against their PartSpecs.
PDF text validation requires `--check-pdf`; KiCad loading requires both `--operation build` and `--check-kicad`.
No model experiment, PDF corpus evaluation, simulator or hardware operation is started by this entry point.

## One result, with separate check states

`passed` means the executed checks produced no failures. `state` communicates the remaining work:

| State | Meaning |
|---|---|
| `failed` | One or more tasks failed; inspect the prioritized findings |
| `needs_review` | Executed checks passed, but evidence, inference, footprint or circuit review work remains |
| `checks_passed` | No outstanding item was reported within the requested scope |

No state asserts physical performance or readiness for manufacture. Each task also records the checks requested and the
states actually observed. Source text, recorded visual review, generated artifacts, KiCad loading and circuit requirements
remain distinct. Rejected/stale review records block generation in that part's task. A circuit using a failed catalog part
gets a dependency failure so it cannot conceal the problem behind otherwise passing connectivity checks.

The project keeps processing independent tasks after a bad file or failed requirement. Invalid manifest structure is
reported before work starts. The completed bundle is published as one new directory; an interrupted publication does not
replace an earlier result. Input fingerprints are captured before and after processing. Changed/unreadable inputs become
failures, and unstable circuit inputs are excluded from the BOM.

## Output layout

```text
work/review-1/
  index.html               Searchable task states and prioritized actions; links to reports and evidence
  project.json             Full report, task input fingerprints and baseline comparison
  project-input.json       Original manifest
  PROJECT.md               Readable handoff
  bom.json                 Component rows plus explicit omitted-circuit reasons
  bom.csv                  The same component inventory for spreadsheets
  sym-lib-table            Only when generated symbols are available
  fp-lib-table             Only when generated footprints are available
  parts/<id>/
    partspec.json
    checks.json
    handoff.json
    review-input.json
    REVIEW.md
    evidence/              Supplied inventory, copied page images/text/contact sheets and gallery
    library/               Successfully generated symbol/footprint files, when requested
  circuits/<id>/
    checks.json
    circuit.json           When a usable circuit document was available
    import.json            For imported netlists
    bindings.json          For imported netlists
    netlist.xml            Original XML, when conversion succeeded
```

Failed jobs can have only a findings file; absence is not silently treated as success. Source PDFs are not copied.
Copied evidence pages remain linked from the bundle's HTML gallery. Absolute paths in machine reports record their
publication location; the HTML links and generated library tables use relative paths so the folder can be moved together.

The concise MCP/CLI response includes totals, failed task IDs, output paths and the first 20 open items, with an explicit
remaining count. `project.json` always contains every item. Inference warnings remain in raw findings; the action queue
groups that work under the part's review actions instead of repeating one warning per pin.

## BOM and KiCad libraries

The BOM is an inventory with one row per reference in each circuit; it does not infer board quantities or buying decisions.
It includes population, part identity, SI passive value, tolerance, voltage rating, exported footprint and any exact catalog
match. DNP rows remain visible with `populated: false`; they do not inflate capacitance checks. Generic passives without an
orderable MPN keep that column empty. Literal values are retained in JSON; CSV formula-like strings are escaped for spreadsheets.

Circuits with failed connectivity are omitted from the BOM and named in `omitted_circuits`. Failed explicit requirements
can still have an inventory: the circuit document records what exists, and the report records why it fails. A generated
footprint is listed separately from the imported footprint; the tool never silently substitutes one for the other.

Library tables contain only files from successful catalog tasks. Their URIs use `${KIPRJMOD}/parts/...` and nicknames match
the generated symbol-to-footprint references. Place the bundle's contents at a KiCad project root, or adapt those relative
URIs when incorporating it elsewhere. Merge table entries into existing tables instead of replacing other libraries.
The tool itself does not modify any existing KiCad project.

## Rework and compare

Edit the original PartSpecs, bindings or circuit requirements, then publish a new output directory. Use the prior result
as a baseline:

```bash
kicad-partspec project PROJECT.json --workspace PROJECT_ROOT --out work/review-2 \
  --baseline work/review-1/project.json --concise
```

The comparison records added/removed tasks, changed input files, changed check scope, new failures and resolved failures.
Removing a task does not count its failures as resolved. Disabling source checks, skipping generation, removing review
inputs or changing a dependent catalog check produces a scope change rather than a claimed repair. All requested work is
executed for the new result; old passes are never reused as though they had just been checked.

To record actual visual work, fill the matching `review-input.json` with attributed, timestamped decisions and point the
part's `decisions_path` at it. The next run verifies its content/scope hashes. If data changed, reconsider the new template;
do not update hashes merely to carry old acceptance forward. This does not run a visual model and does not change a
PartSpec's extraction statuses.
