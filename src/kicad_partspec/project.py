"""One project operation for parts, existing circuits and an inspectable handoff."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kicad_partspec import __version__
from kicad_partspec.artifacts import artifact_directory, read_json, relocate_paths, workspace_path, write_json
from kicad_partspec.decisions import content_hash
from kicad_partspec.findings import FAIL, WARN, Finding
from kicad_partspec.project_reports import bom_csv, bom_rows, compare_reports, library_tables, open_items, project_html, project_markdown
from kicad_partspec.review import review_markdown
from kicad_partspec.verify.quotes import sha256_of


def _jobs(manifest: dict[str, Any], key: str) -> list[dict[str, Any]]:
    jobs = manifest.get(key, [])
    if not isinstance(jobs, list) or len(jobs) > 100:
        raise ValueError(f"{key} must be a list of at most 100 jobs")
    ids: set[str] = set()
    for job in jobs:
        identifier = job.get("id") if isinstance(job, dict) else None
        if (not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", identifier)
                or identifier in ids):
            raise ValueError(f"{key} needs unique IDs: 1..80 letters, digits, underscores or hyphens, starting with a letter/digit")
        ids.add(identifier)
        required = ("spec_path",) if key == "parts" else ("import_path", "circuit_path")
        if sum(field in job for field in required) != 1:
            raise ValueError(f"{key}.{identifier}: provide exactly one of {', '.join(required)}")
        allowed = {"id", *required} | ({"datasheet_path", "evidence_path", "decisions_path"} if key == "parts" else set())
        if set(job) - allowed:
            raise ValueError(f"{key}.{identifier}: unsupported fields {sorted(set(job) - allowed)}")
        for field, value in job.items():
            if field != "id" and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{key}.{identifier}.{field} must be a non-empty workspace path")
    return jobs


def _evidence_assets(manifest: Any) -> list[str]:
    if not isinstance(manifest, dict) or manifest.get("schema") != "partspec.evidence/v1" or not isinstance(manifest.get("pages"), list):
        raise ValueError("use an evidence manifest produced by prepare")
    files = []
    if not isinstance(manifest.get("pdf"), str) or manifest.get("page_count") != len(manifest["pages"]):
        raise ValueError("evidence needs its PDF name and the complete page count")
    for index, page in enumerate(manifest["pages"], 1):
        if (not isinstance(page, dict) or type(page.get("page")) is not int or page["page"] != index
                or page.get("text_quality") not in ("searchable", "sparse", "broken")
                or not isinstance(page.get("topics"), list) or any(not isinstance(topic, str) for topic in page["topics"])
                or not isinstance(page.get("text_file"), str) or "preview" not in page):
            raise ValueError("evidence must contain a complete ordered inventory from prepare")
        files.extend(page[field] for field in ("text_file", "preview") if page.get(field) is not None)
    sheets = manifest.get("contact_sheets", [])
    if not isinstance(sheets, list):
        raise ValueError("contact_sheets must be a list")
    files.extend(sheets)
    if any(not isinstance(value, str) or not value or Path(value).is_absolute() for value in files):
        raise ValueError("evidence assets must use relative paths inside their evidence directory")
    return sorted(set(files))


def _inputs(job: dict[str, Any], kind: str, workspace: Path, check_pdf: bool) -> dict[str, Any]:
    """Hash inputs actually used, including referenced specs and existing evidence assets."""
    fingerprints: dict[str, Any] = {}

    def capture(value: str, boundary: Path = workspace) -> Path | None:
        try:
            path = workspace_path(boundary, value)
            name = path.relative_to(workspace).as_posix()
            fingerprints[name] = {"sha256": sha256_of(path)}
            return path
        except (OSError, ValueError, RuntimeError) as exc:
            fingerprints[value] = {"error": str(exc)}
            return None

    keys = ("spec_path", "evidence_path", "decisions_path") if kind == "part" else ("import_path", "circuit_path")
    if kind == "part" and check_pdf:
        keys += ("datasheet_path",)
    for key in keys:
        if key not in job:
            continue
        path = capture(job[key])
        if path is None or key not in ("evidence_path", "import_path"):
            continue
        try:
            document = read_json(path)
            if key == "evidence_path":
                for asset in _evidence_assets(document):
                    capture(asset, path.parent)
            else:
                if not isinstance(document, dict) or not isinstance(document.get("bindings"), dict):
                    raise ValueError("an import manifest needs a bindings object")
                netlist = document.get("netlist_path")
                if not isinstance(netlist, str) or not netlist:
                    raise ValueError("an import manifest needs netlist_path")
                capture(netlist)
                for binding in document["bindings"].values():
                    if isinstance(binding, dict) and "spec_path" in binding:
                        if not isinstance(binding["spec_path"], str):
                            raise ValueError("spec_path must be a string")
                        capture(binding["spec_path"])
        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
            fingerprints[path.relative_to(workspace).as_posix()]["error"] = str(exc)
    return fingerprints


def _attach_evidence(path: Path, directory: Path, packet: dict[str, Any]) -> dict[str, Any]:
    from kicad_partspec.documents import _gallery

    manifest = read_json(path)
    assets = _evidence_assets(manifest)
    directory.mkdir()
    for relative in assets:
        source = workspace_path(path.parent, relative)
        target = workspace_path(directory, relative)
        if source.suffix.lower() == ".pdf":
            raise ValueError("PDFs are source documents, not evidence image/text assets")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    write_json(directory / "manifest.json", manifest)
    _gallery(directory, manifest)
    return relocate_paths(packet, path.parent, directory)


def _baseline(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or value.get("schema") != "partspec.project-report/v1" or not isinstance(value.get("tasks"), list):
        raise ValueError("baseline must be project.json from an earlier project operation")
    seen = set()
    for task in value["tasks"]:
        if (not isinstance(task, dict) or not isinstance(task.get("id"), str) or task["id"] in seen
                or not isinstance(task.get("inputs"), dict) or not isinstance(task.get("findings"), list)
                or not isinstance(task.get("requested_checks"), dict)):
            raise ValueError("baseline has malformed or duplicate task records")
        seen.add(task["id"])
        if any(not isinstance(f, dict) or not isinstance(f.get("id"), str) or not isinstance(f.get("path", ""), str)
               for f in task["findings"]):
            raise ValueError("baseline has malformed findings")
    return value


def _finish_task(task: dict[str, Any], job: dict[str, Any], workspace: Path, check_pdf: bool) -> None:
    after = _inputs(job, task["kind"], workspace, check_pdf)
    task["checks"]["input_stability"] = "passed" if after == task["inputs"] else "failed"
    if after != task["inputs"]:
        task["findings"].append(Finding("project.inputs_changed", FAIL,
                                        "inputs changed while processing; retry from stable copies before using these results").to_dict())
    for path, fingerprint in task["inputs"].items():
        if fingerprint.get("error"):
            task["checks"]["input_stability"] = "failed"
            task["findings"].append(Finding("project.input_unreadable", FAIL, fingerprint["error"], path=path).to_dict())
    task["input_digest"] = content_hash(task["inputs"])
    task["passed"] = not any(f["status"] == FAIL for f in task["findings"])
    task["state"] = "failed" if not task["passed"] else "needs_review" if open_items([task]) else "checks_passed"


def run_project(
    manifest: Any, *, workspace: Path, out: Path, operation: str = "review", check_pdf: bool = False,
    check_kicad: bool = False, baseline: Any = None,
) -> dict[str, Any]:
    from kicad_partspec import api

    if not isinstance(manifest, dict) or manifest.get("schema") != "partspec.project/v1":
        raise ValueError("use a partspec.project/v1 manifest with name, parts and/or circuits")
    if set(manifest) - {"schema", "name", "parts", "circuits"}:
        raise ValueError(f"unsupported project fields: {sorted(set(manifest) - {'schema', 'name', 'parts', 'circuits'})}")
    name = manifest.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("project name must be a non-empty string")
    if operation not in ("review", "build") or (check_kicad and operation != "build"):
        raise ValueError("operation must be review or build; check_kicad requires build")
    parts, circuits = _jobs(manifest, "parts"), _jobs(manifest, "circuits")
    if not parts and not circuits:
        raise ValueError("a project needs at least one part or circuit")
    previous = _baseline(baseline)
    workspace = workspace.resolve()
    out = workspace_path(workspace, str(out))
    snapshots = {f"{kind}:{job['id']}": _inputs(job, kind, workspace, check_pdf)
                 for kind, jobs in (("part", parts), ("circuit", circuits)) for job in jobs}
    tasks: list[dict[str, Any]] = []
    catalog: dict[str, dict[str, Any]] = {}
    libraries: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    omissions: list[dict[str, str]] = []
    with artifact_directory(out) as staging:
        write_json(staging / "project-input.json", manifest)
        effective_parts = [{key: value for key, value in job.items() if check_pdf or key != "datasheet_path"} for job in parts]
        batch = api.batch({"schema": "partspec.batch/v1", "jobs": effective_parts}, workspace=workspace,
                          operation=operation, out=staging / "parts", check_kicad=check_kicad) if parts else {"items": []}
        by_id = {item["id"]: item for item in batch.get("items", [])}
        for job in parts:
            identifier = job["id"]
            directory = staging / "parts" / identifier
            directory.mkdir(parents=True, exist_ok=True)
            result = by_id.get(identifier, batch)
            checks_path = directory / "checks.json"
            details = read_json(checks_path) if checks_path.is_file() else result
            findings = details.get("findings", [{"status": FAIL, **item} for item in details.get("failed", [])])
            packet_path = directory / "handoff.json"
            packet = read_json(packet_path) if packet_path.is_file() else None
            task = {"id": f"part:{identifier}", "kind": "part", "inputs": snapshots[f"part:{identifier}"],
                    "findings": list(findings), "checks": result.get("checks", {"input_checks": "failed"}),
                    "actions": result.get("actions", []), "review_counts": result.get("review_counts", {}),
                    "files": result.get("files", []), "report_path": f"parts/{identifier}/REVIEW.md" if packet else f"parts/{identifier}/checks.json",
                    "requested_checks": {"partspec": True, "source_text": bool(check_pdf and job.get("datasheet_path")),
                                         "evidence": bool(job.get("evidence_path")), "decisions": bool(job.get("decisions_path")),
                                         "generation": operation == "build", "kicad_load": check_kicad}}
            if packet is not None and job.get("evidence_path"):
                try:
                    packet = _attach_evidence(workspace_path(workspace, job["evidence_path"]), directory / "evidence", packet)
                    task["evidence_path"] = f"parts/{identifier}/evidence/index.html"
                    write_json(packet_path, packet)
                    (directory / "REVIEW.md").write_text(review_markdown(packet), encoding="utf-8")
                except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
                    task["findings"].append(Finding("project.evidence_copy", FAIL, str(exc)).to_dict())
                    if (directory / "evidence").exists():
                        shutil.rmtree(directory / "evidence")
            _finish_task(task, job, workspace, check_pdf)
            write_json(checks_path, {"passed": task["passed"], "findings": task["findings"]})
            if packet is not None:
                packet["passed"] = task["passed"]
                packet["findings"] = task["findings"]
                write_json(packet_path, packet)
                (directory / "REVIEW.md").write_text(review_markdown(packet), encoding="utf-8")
            spec_path = directory / "partspec.json"
            if spec_path.is_file():
                spec = read_json(spec_path)
                entry = {"id": identifier, "passed": task["passed"], "symbol": "", "footprint": "",
                         "scope": task["requested_checks"]}
                if task["passed"]:
                    for filename in result.get("files", []):
                        path = Path(filename)
                        if path.suffix in (".kicad_sym", ".kicad_mod") and path.is_file():
                            entry["symbol" if path.suffix == ".kicad_sym" else "footprint"] = path.relative_to(staging).as_posix()
                catalog.setdefault(content_hash(spec), entry)
                libraries[identifier] = entry
            tasks.append(task)
        if parts:
            batch["passed"] = all(task["passed"] for task in tasks)
            batch["succeeded"] = sum(task["passed"] for task in tasks)
            batch["failed_jobs"] = [task["id"].split(":", 1)[1] for task in tasks if not task["passed"]]
            batch["project_checks_applied"] = True
            batch["items"] = [{"id": task["id"].split(":", 1)[1], "passed": task["passed"],
                               "findings": task["findings"], "checks": task["checks"], "actions": task["actions"]} for task in tasks]
            write_json(staging / "parts" / "batch.json", batch)
        for job in circuits:
            identifier = job["id"]
            directory = staging / "circuits" / identifier
            document = None
            first_row = len(rows)
            try:
                source = workspace_path(workspace, job.get("import_path") or job["circuit_path"])
                data = read_json(source)
                if "import_path" in job:
                    result = api.circuit_import(data, workspace=workspace, out=directory)
                    if (directory / "circuit.json").is_file():
                        document = read_json(directory / "circuit.json")
                else:
                    result = api.circuit_check(data)
                    directory.mkdir(parents=True)
                    write_json(directory / "circuit.json", data)
                    document = data
            except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
                result = {"passed": False, "findings": [Finding("project.circuit_input", FAIL, str(exc)).to_dict()]}
            directory.mkdir(parents=True, exist_ok=True)
            task = {"id": f"circuit:{identifier}", "kind": "circuit", "inputs": snapshots[f"circuit:{identifier}"],
                    "findings": result.get("findings", []), "checks": result.get("coverage", {"connectivity": "not_run"}),
                    "requirements": result.get("requirements", []), "actions": [],
                    "files": [str(directory / "checks.json")], "report_path": f"circuits/{identifier}/checks.json",
                    "requested_checks": {"connectivity": True, "requirements": True, "import": "import_path" in job,
                                         "catalog_checks": {}}}
            if document is not None and task["checks"].get("connectivity") == "passed":
                part_rows = bom_rows(document, identifier, catalog)
                rows.extend(part_rows)
                for row in part_rows:
                    if row["kind"] != "part":
                        continue
                    matched = catalog.get(row["spec_sha256"])
                    if matched is None:
                        task["findings"].append(Finding("project.uncatalogued_part", WARN,
                                                        f'{row["ref"]} has no identical PartSpec in the project part catalog; add it for evidence review and library generation',
                                                        path=row["ref"]).to_dict())
                    elif not matched["passed"]:
                        task["findings"].append(Finding("project.part_blocked", FAIL,
                                                        f'{row["ref"]} uses catalog part {matched["id"]}, whose checks or review failed; resolve that part first',
                                                        path=row["ref"]).to_dict())
                    if matched is not None:
                        task["requested_checks"]["catalog_checks"][matched["id"]] = matched["scope"]
            else:
                omissions.append({"circuit": identifier, "reason": "No circuit with passing connectivity checks was available."})
            _finish_task(task, job, workspace, check_pdf)
            if task["checks"]["input_stability"] == "failed" and len(rows) > first_row:
                del rows[first_row:]
                omissions.append({"circuit": identifier, "reason": "Inputs were unreadable or changed during processing."})
            write_json(directory / "checks.json", task)
            tasks.append(task)
        todo = open_items(tasks)
        report: dict[str, Any] = {
            "schema": "partspec.project-report/v1", "name": name, "engine_version": __version__,
            "created_at": datetime.now(timezone.utc).isoformat(), "passed": all(task["passed"] for task in tasks),
            "state": "failed" if any(not task["passed"] for task in tasks) else "needs_review" if todo else "checks_passed",
            "options": {"operation": operation, "check_pdf": check_pdf, "check_kicad": check_kicad},
            "summary": {"tasks": len(tasks), "failed_tasks": sum(not task["passed"] for task in tasks),
                        "open_items": len(todo), "bom_rows": len(rows), "bom_omitted_circuits": len(omissions)},
            "tasks": tasks, "open_items": todo, "changes": None,
        }
        if previous is not None:
            report["changes"] = compare_reports(report, previous)
        write_json(staging / "bom.json", {"rows": rows, "omitted_circuits": omissions,
                                         "scope": "One row per circuit reference; population is explicit. This is not a procurement list."})
        (staging / "bom.csv").write_text(bom_csv(rows), encoding="utf-8")
        tables = library_tables(libraries)
        for filename, text in tables.items():
            (staging / filename).write_text(text, encoding="utf-8")
        report["files"] = [str(out / filename) for filename in ("project.json", "project-input.json", "index.html", "PROJECT.md", "bom.json", "bom.csv", *tables)]
        # Child operations used stable paths inside staging; publish their reports with final paths.
        for filename in ("checks.json", "handoff.json", "batch.json", "import.json"):
            for path in staging.rglob(filename):
                write_json(path, relocate_paths(read_json(path), staging, out))
        for path in staging.rglob("REVIEW.md"):
            path.write_text(path.read_text(encoding="utf-8").replace(str(staging) + "/", str(out) + "/"), encoding="utf-8")
        report = relocate_paths(report, staging, out)
        write_json(staging / "project.json", report)
        (staging / "PROJECT.md").write_text(project_markdown(report), encoding="utf-8")
        (staging / "index.html").write_text(project_html(report), encoding="utf-8")
    return report
