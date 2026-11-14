"""Command line entry point for evidence, part libraries and circuit requirements."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kicad_partspec import api
from kicad_partspec.artifacts import read_json
from kicad_partspec.findings import Finding, failed


_READ_FAILED = object()


def _read_json(path: Path) -> object:
    try:
        return read_json(path)
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"passed": False, "error": f"cannot read {path}: {exc}"}), file=sys.stderr)
    except ValueError as exc:
        print(json.dumps({"passed": False, "error": f"{path} is not valid JSON: {exc}"}), file=sys.stderr)
    return _READ_FAILED


def _report(findings: list[Finding], files: list[str] | None = None, *, concise: bool = False) -> int:
    if concise:
        summary = api.summarize(findings, files, api.CONCISE)
        print(json.dumps(summary, indent=2))
        return 0 if summary["passed"] else 1
    report: dict[str, object] = {"passed": not failed(findings)}
    if files is not None:
        report["files"] = files
    report["findings"] = [item.to_dict() for item in findings]
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


def _document_report(report: dict) -> int:
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kicad-partspec")
    sub = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--concise", action="store_true", help="failures in full, warnings only counted by kind")

    prepare = sub.add_parser("prepare", help="index every PDF page and make a bounded visual overview")
    prepare.add_argument("datasheet", type=Path)
    prepare.add_argument("--out", type=Path, required=True, help="new directory for the evidence packet")
    prepare.add_argument("--term", action="append", default=[], help="part number or drawing code; repeat as needed")
    prepare.add_argument("--preview-limit", type=int, default=24, help="0..32 previews; 0 only indexes text")

    pages = sub.add_parser("read-pages", help="read several PDF pages with text, images and optional crops")
    pages.add_argument("datasheet", type=Path)
    pages.add_argument("--pages", required=True, help="PDF page indexes, for example 1,7-9,12 (at most 32)")
    pages.add_argument("--out", type=Path, required=True, help="new directory for the selected pages")
    pages.add_argument("--dpi", type=int, default=180)
    pages.add_argument("--crop", type=float, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    pages.add_argument("--sha256", help="expected PDF hash from prepare")

    review = sub.add_parser("review", help="report checks, evidence pages and remaining review work")
    review.add_argument("spec", type=Path)
    review.add_argument("--datasheet", type=Path, help="also execute PDF hash and quote checks")
    review.add_argument("--evidence", type=Path, help="manifest.json from prepare")
    review.add_argument("--decisions", type=Path, help="attributed decisions from a matching review-input.json")
    review.add_argument("--out", type=Path, help="new directory for handoff, review template and Markdown")

    batch = sub.add_parser("batch", help="validate, review or build multiple PartSpecs in one call")
    batch.add_argument("manifest", type=Path)
    batch.add_argument("--operation", choices=("validate", "review", "build"), default="review")
    batch.add_argument("--workspace", type=Path, default=None, help="path boundary; defaults to the manifest directory")
    batch.add_argument("--out", type=Path, help="new directory inside the workspace; required for build")
    batch.add_argument("--check-kicad", action="store_true", help="explicitly load generated files with KiCad")

    circuit = sub.add_parser("circuit-check", help="check physical-pin nets and explicit circuit requirements")
    circuit.add_argument("plan", type=Path)

    imported = sub.add_parser("circuit-import", help="bind an exported KiCad XML netlist to existing PartSpecs")
    imported.add_argument("manifest", type=Path)
    imported.add_argument("--workspace", type=Path, help="path boundary; defaults to the manifest directory")
    imported.add_argument("--out", type=Path, help="new directory inside the workspace; otherwise return the circuit inline")

    project = sub.add_parser("project", parents=[common], help="process a whole project and publish reports, BOM and library tables")
    project.add_argument("manifest", type=Path)
    project.add_argument("--workspace", type=Path, help="path boundary; defaults to the manifest directory")
    project.add_argument("--out", type=Path, required=True, help="new project bundle directory inside the workspace")
    project.add_argument("--operation", choices=("review", "build"), default="review")
    project.add_argument("--check-pdf", action="store_true", help="explicitly check supplied PDFs and their quotes")
    project.add_argument("--check-kicad", action="store_true", help="explicitly load generated libraries; requires build")
    project.add_argument("--baseline", type=Path, help="project.json from a previous bundle, inside the workspace")

    validate = sub.add_parser("validate", parents=[common], help="check a PartSpec JSON file")
    validate.add_argument("spec", type=Path)
    validate.add_argument("--datasheet", type=Path, help="also check every quote against this datasheet PDF")

    build = sub.add_parser(
        "build",
        parents=[common],
        help="generate a symbol (and a footprint when the land pattern allows) and verify them",
    )
    build.add_argument("spec", type=Path)
    build.add_argument("--out", type=Path, required=True, help="directory for the generated files")
    build.add_argument("--no-kicad", action="store_true", help="skip loading the result with kicad-cli")
    build.add_argument("--lib-name", default="partspec", help="footprint library nickname (default: partspec)")

    verify = sub.add_parser("verify", parents=[common], help="check existing symbol/footprint files against a PartSpec")
    verify.add_argument("spec", type=Path)
    verify.add_argument("--symbol", type=Path)
    verify.add_argument("--footprint", type=Path)
    verify.add_argument("--no-kicad", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "prepare":
        return _document_report(api.prepare_datasheet(
            args.datasheet, args.out, terms=args.term, preview_limit=args.preview_limit,
        ))
    if args.command == "read-pages":
        return _document_report(api.read_datasheet_pages(
            args.datasheet, args.pages, args.out, dpi=args.dpi, crop=args.crop, expected_sha256=args.sha256,
        ))
    if args.command in ("batch", "circuit-check", "circuit-import", "project"):
        data = _read_json(args.plan if args.command == "circuit-check" else args.manifest)
        if data is _READ_FAILED:
            return 2
        if args.command == "circuit-check":
            return _document_report(api.circuit_check(data))
        if args.command == "circuit-import":
            return _document_report(api.circuit_import(
                data, workspace=args.workspace or args.manifest.resolve().parent, out=args.out,
            ))
        if args.command == "project":
            from kicad_partspec.artifacts import workspace_path

            root = args.workspace or args.manifest.resolve().parent
            try:
                baseline_path = workspace_path(root, str(args.baseline)) if args.baseline else None
            except ValueError as exc:
                return _document_report({"passed": False, "error": str(exc)})
            baseline = _read_json(baseline_path) if baseline_path else None
            if baseline is _READ_FAILED:
                return 2
            return _document_report(api.project(
                data, workspace=root, out=args.out, operation=args.operation, check_pdf=args.check_pdf,
                check_kicad=args.check_kicad, baseline=baseline,
                response_format=api.CONCISE if args.concise else api.DETAILED,
            ))
        return _document_report(api.batch(
            data, workspace=args.workspace or args.manifest.resolve().parent,
            operation=args.operation, out=args.out, check_kicad=args.check_kicad,
        ))
    data = _read_json(args.spec)
    if data is _READ_FAILED:
        return 2
    if args.command == "review":
        evidence = _read_json(args.evidence) if args.evidence else None
        if args.evidence and evidence is _READ_FAILED:
            return 2
        decisions = _read_json(args.decisions) if args.decisions else None
        if args.decisions and decisions is _READ_FAILED:
            return 2
        return _document_report(api.review(
            data, datasheet=args.datasheet, evidence=evidence, out=args.out,
            evidence_directory=args.evidence.resolve().parent if args.evidence else None,
            decisions=decisions,
        ))
    if args.command == "build":
        result = api.build(data, args.out, lib_name=args.lib_name, check_kicad=not args.no_kicad)
        return _report(result.findings, result.files, concise=args.concise)
    if args.command == "verify":
        return _report(
            api.verify_files(data, symbol=args.symbol, footprint=args.footprint, check_kicad=not args.no_kicad),
            concise=args.concise,
        )
    return _report(api.validate(data, args.datasheet), concise=args.concise)


if __name__ == "__main__":
    raise SystemExit(main())
