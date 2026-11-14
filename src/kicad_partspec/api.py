"""Operations shared by the CLI and the MCP server.

Everything here returns findings instead of raising on bad input, so callers
(and agents) always get the full list of problems in one pass.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kicad_partspec.artifacts import artifact_directory, read_json, workspace_path, write_json
from kicad_partspec.findings import FAIL, WARN, Finding, failed
from kicad_partspec.gen.footprint import footprint_name, render_footprint, skip_reason
from kicad_partspec.gen.symbol import render_library, unit_groups
from kicad_partspec.spec import load_spec
from kicad_partspec.verify import verify_spec
from kicad_partspec.verify.footprint_checks import check_footprint
from kicad_partspec.verify.kicad_checks import check_footprint_loads, check_symbol_loads
from kicad_partspec.verify.quotes import check_quotes, document_number, first_page, page_texts, sha256_of
from kicad_partspec.verify.symbol_checks import check_symbol

CONCISE = "concise"
DETAILED = "detailed"


@dataclass
class Result:
    findings: list[Finding]
    files: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not failed(self.findings)


def file_stem(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._+-]", "_", name)


def validate(data: Any, datasheet: Path | None = None) -> list[Finding]:
    """Spec-layer checks, plus the source check when the datasheet PDF is given."""
    findings = verify_spec(data)
    if datasheet is None:
        return findings
    parsed, _ = load_spec(data)
    if parsed is None:
        return findings
    if not datasheet.is_file():
        return [
            *findings,
            Finding("prov.datasheet_unreadable", FAIL, f"the datasheet file {datasheet} does not exist."),
        ]
    declared = (data.get("datasheet") or {}).get("sha256") if isinstance(data.get("datasheet"), dict) else None
    try:
        actual = sha256_of(datasheet)
    except OSError as exc:
        return [*findings, Finding("prov.datasheet_unreadable", FAIL, f"cannot read {datasheet}: {exc}")]
    revision = (data.get("datasheet") or {}).get("revision") if isinstance(data.get("datasheet"), dict) else None
    if declared != actual:
        number = document_number(revision if isinstance(revision, str) else "")
        try:
            rebuilt = number is not None and number in first_page(datasheet)
        except (OSError, UnicodeError, RuntimeError) as exc:
            return [*findings, Finding("prov.datasheet_unreadable", FAIL, str(exc))]
        findings.append(
            Finding(
                "prov.datasheet_rebuilt" if rebuilt else "prov.datasheet_sha_mismatch",
                WARN if rebuilt else FAIL,
                f"quotes checked against a same-revision rebuild of {number or 'this datasheet'}: the vendor "
                "re-issued the PDF, so datasheet.sha256 does not match any local file. Do not rewrite the "
                "spec's sha256 — it records the file the gold was built from."
                if rebuilt
                else f"datasheet.sha256 is {declared!r} but the PDF's SHA-256 is {actual}; set datasheet.sha256 to that value.",
                path="datasheet.sha256",
                expected=actual,
                actual=declared,
            )
        )
    try:
        findings.extend(check_quotes(data, page_texts(datasheet)))
    except (OSError, UnicodeError, RuntimeError) as exc:
        findings.append(Finding("prov.datasheet_unreadable", FAIL, f"could not read the datasheet text: {exc}."))
    return findings


def build(data: Any, out: Path, *, lib_name: str = "partspec", check_kicad: bool = True) -> Result:
    """Generate and verify the symbol and, when the land pattern allows, the footprint."""
    findings = verify_spec(data)
    if not re.fullmatch(r"[A-Za-z0-9_+-][A-Za-z0-9_.+-]*", lib_name):
        findings.append(Finding("build.library_name", FAIL,
                                "lib_name must be a library nickname, not a path; use letters, digits, _, +, - and ."))
    if failed(findings):
        return Result(findings)  # never generate from a spec that fails its own checks
    spec, _ = load_spec(data)
    assert spec is not None
    out.mkdir(parents=True, exist_ok=True)
    files: list[str] = []

    footprint_ref: str | None = None
    reason = skip_reason(spec)
    if reason is None:
        name = footprint_name(spec)
        text = render_footprint(spec, name)
        pretty = out / f"{lib_name}.pretty"
        pretty.mkdir(exist_ok=True)
        target = pretty / f"{file_stem(name)}.kicad_mod"
        target.write_text(text, encoding="utf-8")
        files.append(str(target))
        footprint_ref = f"{lib_name}:{name}"
        findings.extend(check_footprint(spec, text))
        if check_kicad:
            findings.extend(check_footprint_loads(pretty, name=file_stem(name)))
    else:
        findings.append(Finding("footprint.skipped", WARN, f"no footprint was generated: {reason}."))

    symbol_text = render_library(spec, footprint_ref)
    symbol_file = out / f"{file_stem(spec.mpn)}.kicad_sym"
    symbol_file.write_text(symbol_text, encoding="utf-8")
    files.insert(0, str(symbol_file))
    findings.extend(check_symbol(spec, symbol_text, expected_footprint=footprint_ref or ""))
    if check_kicad:
        findings.extend(check_symbol_loads(symbol_file, expected_units=len(unit_groups(spec.pins))))
    return Result(findings, files)


def verify_files(
    data: Any,
    *,
    symbol: Path | None = None,
    footprint: Path | None = None,
    check_kicad: bool = True,
) -> list[Finding]:
    """Check existing symbol and/or footprint files against a spec (they may come from anywhere)."""
    findings = verify_spec(data)
    if failed(findings):
        return findings
    spec, _ = load_spec(data)
    assert spec is not None
    if symbol is None and footprint is None:
        return [*findings, Finding("verify.nothing", FAIL, "pass a symbol file, a footprint file, or both.")]
    if symbol is not None:
        try:
            text = symbol.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(Finding("verify.unreadable", FAIL, f"cannot read {symbol}: {exc}."))
        else:
            findings.extend(check_symbol(spec, text))
            if check_kicad:
                findings.extend(check_symbol_loads(symbol, expected_units=len(unit_groups(spec.pins))))
    if footprint is not None:
        try:
            text = footprint.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(Finding("verify.unreadable", FAIL, f"cannot read {footprint}: {exc}."))
        else:
            findings.extend(check_footprint(spec, text))
            if check_kicad:
                with tempfile.TemporaryDirectory(prefix="partspec-pretty-") as temporary:
                    pretty = Path(temporary) / "check.pretty"
                    pretty.mkdir()
                    shutil.copy(footprint, pretty / footprint.name)
                    findings.extend(check_footprint_loads(pretty, name=footprint.stem))
    return findings


def summarize(
    result_findings: list[Finding], files: list[str] | None = None, response_format: str = CONCISE
) -> dict[str, Any]:
    """A result an agent can act on: failures first; detail only on request."""
    failures = [item for item in result_findings if item.status == FAIL]
    warnings = [item for item in result_findings if item.status == WARN]
    report: dict[str, Any] = {
        "passed": not failures,
        "failures": len(failures),
        "warnings": len(warnings),
    }
    if files is not None:
        report["files"] = files
    if response_format == DETAILED:
        report["findings"] = [item.to_dict() for item in result_findings]
    else:
        report["failed"] = [{"id": item.id, "path": item.path, "message": item.message} for item in failures]
        if warnings:
            counts: dict[str, int] = {}
            for item in warnings:
                counts[item.id] = counts.get(item.id, 0) + 1
            report["warning_summary"] = counts
    return report


def _operation_error(operation: str, error: Exception) -> dict[str, Any]:
    return summarize([Finding(f"{operation}.failed", FAIL, str(error))], response_format=DETAILED)


def prepare_datasheet(
    datasheet: Path, out: Path, *, terms: list[str] | None = None, preview_limit: int = 24,
) -> dict[str, Any]:
    from kicad_partspec.documents import prepare

    try:
        return prepare(datasheet, out, terms=terms, preview_limit=preview_limit)
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        return _operation_error("prepare", exc)


def read_datasheet_pages(
    datasheet: Path, pages: str, out: Path, *, dpi: int = 180, crop: list[float] | None = None,
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    from kicad_partspec.documents import read_pages

    try:
        return read_pages(datasheet, pages, out, dpi=dpi, crop=crop, expected_sha256=expected_sha256)
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        return _operation_error("read_pages", exc)


def review(
    data: Any, *, datasheet: Path | None = None, evidence: Any = None, out: Path | None = None,
    evidence_directory: Path | None = None,
    decisions: Any = None,
) -> dict[str, Any]:
    from kicad_partspec.review import review_markdown, review_packet

    packet = review_packet(
        data, validate(data, datasheet), source_checked=datasheet is not None,
        evidence=evidence, evidence_directory=evidence_directory, decisions=decisions,
    )
    if out is not None:
        try:
            with artifact_directory(out) as staging:
                write_json(staging / "handoff.json", packet)
                write_json(staging / "review-input.json", packet["review_input"])
                (staging / "REVIEW.md").write_text(review_markdown(packet), encoding="utf-8")
            packet["files"] = [str(out / name) for name in ("handoff.json", "REVIEW.md", "review-input.json")]
        except (OSError, ValueError) as exc:
            return _operation_error("review", exc)
    return packet


def batch(
    manifest: Any, *, workspace: Path, operation: str = "review", out: Path | None = None,
    check_kicad: bool = False,
) -> dict[str, Any]:
    from kicad_partspec.workflow import run_batch

    try:
        return run_batch(manifest, workspace=workspace, operation=operation, out=out, check_kicad=check_kicad)
    except (OSError, ValueError, RuntimeError) as exc:
        return _operation_error("batch", exc)


def circuit_check(data: Any) -> dict[str, Any]:
    from kicad_partspec.circuit import check_circuit

    return check_circuit(data)


def circuit_import(manifest: Any, *, workspace: Path, out: Path | None = None) -> dict[str, Any]:
    """Bind an existing XML export to local PartSpecs and explicit passive metadata."""
    from kicad_partspec.decisions import content_hash
    from kicad_partspec.netlist import MAX_NETLIST_BYTES, import_xml

    try:
        if not isinstance(manifest, dict) or manifest.get("schema") != "partspec.circuit-import/v1":
            raise ValueError("use a partspec.circuit-import/v1 manifest with netlist_path and bindings")
        netlist_path, bindings = manifest.get("netlist_path"), manifest.get("bindings")
        if not isinstance(netlist_path, str) or not netlist_path.strip() or not isinstance(bindings, dict):
            raise ValueError("netlist_path must name an exported XML file; bindings must be an object keyed by reference")
        source = workspace_path(workspace, netlist_path)
        with source.open("rb") as stream:
            xml = stream.read(MAX_NETLIST_BYTES + 1)
        specs = {}
        documents: dict[Path, Any] = {}
        for ref, binding in bindings.items():
            if isinstance(binding, dict) and "spec_path" in binding:
                if not isinstance(binding["spec_path"], str) or not binding["spec_path"].strip():
                    raise ValueError(f"{ref}.spec_path must be a non-empty path inside the workspace")
                path = workspace_path(workspace, binding["spec_path"])
                if path not in documents:
                    documents[path] = read_json(path)
                specs[ref] = documents[path]
        circuit, findings = import_xml(
            xml, bindings, specs, requirements=manifest.get("requirements"), unconnected=manifest.get("unconnected"),
        )
        checks = None
        if circuit is not None:
            circuit["imported_from"].update(
                file=str(source), bindings_sha256=content_hash(manifest),
                spec_hashes={ref: content_hash(spec) for ref, spec in specs.items()},
            )
            checks = circuit_check(circuit)
            findings.extend(Finding(**finding) for finding in checks["findings"])
        report = {
            "schema": "partspec.circuit-import-report/v1", **summarize(findings, response_format=DETAILED),
            "circuit_emitted": circuit is not None,
            "coverage": checks["coverage"] if checks else {"connectivity": "not_run", "simulation": "not_run"},
            "requirements": checks["requirements"] if checks else [],
        }
        if out is None:
            report["circuit"] = circuit
        else:
            destination = workspace_path(workspace, str(out))
            names = ["import.json", "bindings.json"]
            if circuit is not None:
                names += ["circuit.json", "netlist.xml"]
            report["files"] = [str(destination / name) for name in names]
            with artifact_directory(destination) as staging:
                write_json(staging / "import.json", report)
                write_json(staging / "bindings.json", manifest)
                if circuit is not None:
                    write_json(staging / "circuit.json", circuit)
                    (staging / "netlist.xml").write_bytes(xml)
        return report
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        return _operation_error("circuit_import", exc)


def project(
    manifest: Any, *, workspace: Path, out: Path, operation: str = "review", check_pdf: bool = False,
    check_kicad: bool = False, baseline: Any = None, response_format: str = CONCISE,
) -> dict[str, Any]:
    from kicad_partspec.project import run_project

    try:
        report = run_project(manifest, workspace=workspace, out=out, operation=operation,
                             check_pdf=check_pdf, check_kicad=check_kicad, baseline=baseline)
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        return _operation_error("project", exc)
    if response_format == DETAILED:
        return report
    return {
        **{key: report[key] for key in ("schema", "name", "passed", "state", "summary", "files")},
        "failed_tasks": [task["id"] for task in report["tasks"] if not task["passed"]],
        "next_actions": report["open_items"][:20], "remaining_actions": max(0, len(report["open_items"]) - 20),
        "changes": None if report["changes"] is None else {
            key: len(value) for key, value in report["changes"].items()
        },
    }
