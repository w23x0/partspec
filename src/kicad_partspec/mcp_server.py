"""MCP server for evidence, library generation, handoff and circuit requirements.

Paths are confined to ``PARTSPEC_WORKSPACE`` (default: the working directory).
A PartSpec can be passed inline or, to save context on large parts, as a file path.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from kicad_partspec import __version__, api
from kicad_partspec.artifacts import read_json

ResponseFormat = Literal["concise", "detailed"]

mcp = MCPServer(
    "PartSpec",
    version=__version__,
    instructions=(
        "Prepare datasheet evidence, extract a PartSpec, and generate KiCad symbols and footprints. "
        "Use partspec_prepare to inventory all pages, partspec_read_pages for bounded visual reading, "
        "and partspec_review for findings and the remaining review queue. Use partspec_project for a complete "
        "parts-and-circuits handoff with reports, BOM and library tables; partspec_batch handles parts alone. "
        "partspec_circuit_import binds an exported KiCad XML netlist to PartSpecs; "
        "partspec_circuit_check checks explicit netlist requirements without running a simulator. "
        "Source text matches do not prove visual bindings or electrical performance. "
        "See the partspec skill for extraction rules. Paths must be inside PARTSPEC_WORKSPACE."
    ),
)

_READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
_WRITES_FILES = ToolAnnotations(
    read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=False
)
_NEW_FILES = ToolAnnotations(
    read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False
)


def workspace() -> Path:
    return Path(os.environ.get("PARTSPEC_WORKSPACE") or Path.cwd()).resolve()


def _path(value: str, *, what: str, must_exist: bool = False) -> Path:
    root = workspace()
    candidate = Path(value).expanduser()
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    if not resolved.is_relative_to(root):
        raise ToolError(f"{what} {value!r} is outside the workspace {root}; use a path inside it.")
    if must_exist and not resolved.exists():
        raise ToolError(f"{what} {value!r} does not exist (looked for {resolved}).")
    return resolved


def _spec(spec_path: str | None, spec: dict[str, Any] | None) -> Any:
    if (spec_path is None) == (spec is None):
        raise ToolError("pass exactly one of spec_path (a JSON file) or spec (the PartSpec object).")
    if spec is not None:
        return spec
    assert spec_path is not None
    return _json_file(spec_path, what="spec_path")


def _json_file(value: str, *, what: str) -> Any:
    path = _path(value, what=what, must_exist=True)
    try:
        return read_json(path)
    except (OSError, UnicodeError) as exc:
        raise ToolError(f"cannot read {path}: {exc}") from exc
    except ValueError as exc:
        raise ToolError(f"{path} is not valid JSON: {exc}") from exc


@mcp.tool(annotations=_NEW_FILES)
def partspec_project(
    out_dir: str, manifest_path: str | None = None, manifest: dict[str, Any] | None = None,
    operation: Literal["review", "build"] = "review", check_pdf: bool = False, check_kicad: bool = False,
    baseline_path: str | None = None, response_format: ResponseFormat = "concise",
) -> dict[str, Any]:
    """Process a partspec.project/v1 manifest into one new, browsable project bundle.

    Pass exactly one of manifest_path or manifest. Parts use the batch job fields; circuits use
    id plus either circuit_path or import_path. All paths resolve inside PARTSPEC_WORKSPACE.
    Outputs include index.html, project.json, per-task reports, evidence copies, BOM and generated
    KiCad library tables. Failures stay visible and independent tasks continue. PDF validation and
    KiCad loading are opt-in; no model, simulation, rendering or hardware test is started.
    baseline_path compares against an earlier project.json; reduced check scope is not a fixed failure.
    Concise output includes the first 20 actions; the full list is saved in project.json.
    """
    if (manifest_path is None) == (manifest is None):
        raise ToolError("pass exactly one of manifest_path or manifest.")
    document = _json_file(manifest_path, what="manifest_path") if manifest_path is not None else manifest
    baseline = _json_file(baseline_path, what="baseline_path") if baseline_path else None
    return api.project(
        document, workspace=workspace(), out=_path(out_dir, what="out_dir"), operation=operation,
        check_pdf=check_pdf, check_kicad=check_kicad, baseline=baseline, response_format=response_format,
    )


@mcp.tool(annotations=_NEW_FILES)
def partspec_prepare(
    datasheet_path: str, out_dir: str, terms: list[str] | None = None, preview_limit: int = 24,
) -> dict[str, Any]:
    """Index ALL PDF pages and create a gallery, text files and labeled contact sheets.

    Pass part numbers or drawing codes in terms. Sparse/broken pages remain in the inventory.
    preview_limit is 0..32; 0 skips image rendering. out_dir must be new. This does not extract a PartSpec.
    """
    return api.prepare_datasheet(
        _path(datasheet_path, what="datasheet_path", must_exist=True), _path(out_dir, what="out_dir"),
        terms=terms, preview_limit=preview_limit,
    )


@mcp.tool(annotations=_NEW_FILES)
def partspec_read_pages(
    datasheet_path: str, pages: str, out_dir: str, dpi: int = 180,
    crop: list[float] | None = None, expected_sha256: str | None = None,
) -> dict[str, Any]:
    """Read up to 32 PDF pages in one call, e.g. pages='1,7-9'. Save images and full page text.

    crop is [left, top, right, bottom] in 0..1 page coordinates; text always covers the full page.
    Returns image paths for the client's image viewer, not a claim that images were inspected.
    Set expected_sha256 from prepare to pin the PDF. out_dir must be new.
    """
    return api.read_datasheet_pages(
        _path(datasheet_path, what="datasheet_path", must_exist=True), pages, _path(out_dir, what="out_dir"),
        dpi=dpi, crop=crop, expected_sha256=expected_sha256,
    )


@mcp.tool(annotations=_NEW_FILES)
def partspec_review(
    spec_path: str | None = None, spec: dict[str, Any] | None = None,
    datasheet_path: str | None = None, evidence_path: str | None = None, out_dir: str | None = None,
    decisions_path: str | None = None,
) -> dict[str, Any]:
    """Group fields and quotes by PDF page, report inferences, blockers and outstanding visual review.

    datasheet_path opts into hash/quote checks. evidence_path is prepare's manifest.json.
    decisions_path supplies attributed review records bound to this PartSpec and review scope.
    With a new out_dir save handoff.json, REVIEW.md and review-input.json for subsequent decisions.
    passed describes executed checks, not readiness for fabrication.
    """
    evidence_file = _path(evidence_path, what="evidence_path", must_exist=True) if evidence_path else None
    return api.review(
        _spec(spec_path, spec),
        datasheet=_path(datasheet_path, what="datasheet_path", must_exist=True) if datasheet_path else None,
        evidence=_json_file(evidence_path, what="evidence_path") if evidence_path else None,
        evidence_directory=evidence_file.parent if evidence_file else None,
        decisions=_json_file(decisions_path, what="decisions_path") if decisions_path else None,
        out=_path(out_dir, what="out_dir") if out_dir else None,
    )


@mcp.tool(annotations=_NEW_FILES)
def partspec_batch(
    manifest_path: str | None = None, manifest: dict[str, Any] | None = None,
    operation: Literal["validate", "review", "build"] = "review", out_dir: str | None = None,
    check_kicad: bool = False,
) -> dict[str, Any]:
    """Process 1..100 jobs from a partspec.batch/v1 manifest; preserve individual failures.

    Pass exactly one of manifest_path or manifest. Each job needs id and spec_path, optionally
    datasheet_path/evidence_path/decisions_path. All nested paths resolve inside PARTSPEC_WORKSPACE.
    out_dir must be new and is required for build. KiCad loading is opt-in.
    """
    if (manifest_path is None) == (manifest is None):
        raise ToolError("pass exactly one of manifest_path or manifest.")
    document = _json_file(manifest_path, what="manifest_path") if manifest_path is not None else manifest
    return api.batch(
        document, workspace=workspace(), operation=operation,
        out=_path(out_dir, what="out_dir") if out_dir else None, check_kicad=check_kicad,
    )


@mcp.tool(annotations=_NEW_FILES)
def partspec_circuit_import(
    manifest_path: str | None = None, manifest: dict[str, Any] | None = None, out_dir: str | None = None,
) -> dict[str, Any]:
    """Import an existing KiCad XML netlist with explicit per-reference PartSpec/passive bindings.

    Pass exactly one of manifest_path or manifest, using schema partspec.circuit-import/v1.
    netlist_path and each bindings[ref].spec_path resolve inside PARTSPEC_WORKSPACE. Generic
    passive values can come from complete EDA labels such as 4k7 or 22uF; tolerance and voltage
    ratings must be supplied. Return the circuit inline or save to a new out_dir, with findings.
    Does not start KiCad, export a schematic, simulate or rewrite the source netlist.
    """
    if (manifest_path is None) == (manifest is None):
        raise ToolError("pass exactly one of manifest_path or manifest.")
    document = _json_file(manifest_path, what="manifest_path") if manifest_path is not None else manifest
    return api.circuit_import(
        document, workspace=workspace(), out=_path(out_dir, what="out_dir") if out_dir else None,
    )


@mcp.tool(annotations=_READ_ONLY)
def partspec_circuit_check(
    circuit_path: str | None = None, circuit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check a partspec.circuit/v1 netlist using physical pin numbers and inline PartSpecs.

    Requirements: same_net, separate_nets, capacitance_between and voltage_rating.
    Minimum capacitance requires tolerance; only directly parallel capacitors are counted.
    No simulator, KiCad process or hardware is used. Pass exactly one of circuit_path or circuit.
    """
    if (circuit_path is None) == (circuit is None):
        raise ToolError("pass exactly one of circuit_path or circuit.")
    document = _json_file(circuit_path, what="circuit_path") if circuit_path is not None else circuit
    return api.circuit_check(document)


@mcp.tool(annotations=_READ_ONLY)
def partspec_validate(
    spec_path: str | None = None,
    spec: dict[str, Any] | None = None,
    datasheet_path: str | None = None,
    response_format: ResponseFormat = "concise",
) -> dict[str, Any]:
    """Check a PartSpec: structure, provenance, pin count, unique pin numbers, KiCad pin types, dimension order.

    With datasheet_path (the PDF) it also confirms the SHA-256 and that every source quote appears on its cited page.
    Fix every entry in "failed" and call again until "passed" is true.
    """
    document = _spec(spec_path, spec)
    datasheet = _path(datasheet_path, what="datasheet_path", must_exist=True) if datasheet_path else None
    return api.summarize(api.validate(document, datasheet), response_format=response_format)


@mcp.tool(annotations=_WRITES_FILES)
def partspec_build(
    out_dir: str,
    spec_path: str | None = None,
    spec: dict[str, Any] | None = None,
    lib_name: str = "partspec",
    check_kicad: bool = True,
    response_format: ResponseFormat = "concise",
) -> dict[str, Any]:
    """Generate a KiCad symbol (and a footprint when the datasheet land pattern is in the spec) and verify them.

    Writes <mpn>.kicad_sym and <lib_name>.pretty/<name>.kicad_mod into out_dir, re-parses them against the spec, and
    loads them with kicad-cli. Nothing is written if the spec itself fails validation.
    """
    document = _spec(spec_path, spec)
    out = _path(out_dir, what="out_dir")
    result = api.build(document, out, lib_name=lib_name, check_kicad=check_kicad)
    return api.summarize(result.findings, result.files, response_format)


@mcp.tool(annotations=_READ_ONLY)
def partspec_verify(
    spec_path: str | None = None,
    spec: dict[str, Any] | None = None,
    symbol_path: str | None = None,
    footprint_path: str | None = None,
    check_kicad: bool = True,
    response_format: ResponseFormat = "concise",
) -> dict[str, Any]:
    """Check existing .kicad_sym and/or .kicad_mod files (from any source) against a PartSpec."""
    document = _spec(spec_path, spec)
    symbol = _path(symbol_path, what="symbol_path", must_exist=True) if symbol_path else None
    footprint = _path(footprint_path, what="footprint_path", must_exist=True) if footprint_path else None
    findings = api.verify_files(document, symbol=symbol, footprint=footprint, check_kicad=check_kicad)
    return api.summarize(findings, response_format=response_format)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
