"""Batch operations with one immutable output directory per part."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from kicad_partspec.artifacts import artifact_directory, read_json, workspace_path, write_json
from kicad_partspec.findings import FAIL, Finding, failed
from kicad_partspec.review import review_markdown, review_packet


def run_batch(
    manifest: Any, *, workspace: Path, operation: str = "review", out: Path | None = None,
    check_kicad: bool = False,
) -> dict[str, Any]:
    from kicad_partspec import api

    if operation not in ("validate", "review", "build"):
        raise ValueError("operation must be validate, review or build")
    if not isinstance(manifest, dict) or manifest.get("schema") != "partspec.batch/v1":
        raise ValueError("use a manifest with schema partspec.batch/v1 and a jobs list")
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= 100:
        raise ValueError("jobs must contain 1..100 objects")
    seen: set[str] = set()
    for job in jobs:
        identifier = job.get("id") if isinstance(job, dict) else None
        if (not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", identifier)
                or identifier in seen):
            raise ValueError("each job needs a unique id using letters, numbers, underscores or hyphens (1..80 characters)")
        seen.add(identifier)
        if not isinstance(job.get("spec_path"), str) or not job["spec_path"].strip():
            raise ValueError(f"job {identifier} needs spec_path")
        for key in ("datasheet_path", "evidence_path", "decisions_path"):
            if job.get(key) is not None and not isinstance(job[key], str):
                raise ValueError(f"job {identifier}.{key} must be a path string")
    if operation == "build" and out is None:
        raise ValueError("build batches require an output directory")
    if out is not None:
        out = workspace_path(workspace, str(out))
        out.mkdir(parents=True, exist_ok=False)
    items = []
    for job in jobs:
        identifier = job["id"]
        files: list[str] = []
        packet = None
        try:
            spec_path = workspace_path(workspace, job["spec_path"])
            data = read_json(spec_path)
            pdf = workspace_path(workspace, job["datasheet_path"]) if job.get("datasheet_path") else None
            evidence_path = (workspace_path(workspace, job["evidence_path"])
                             if operation != "validate" and job.get("evidence_path") else None)
            evidence = read_json(evidence_path) if evidence_path else None
            decisions_path = (workspace_path(workspace, job["decisions_path"])
                              if operation != "validate" and job.get("decisions_path") else None)
            decisions = read_json(decisions_path) if decisions_path else None
            findings = api.validate(data, pdf)
            if operation != "validate":
                packet = review_packet(
                    data, findings, source_checked=pdf is not None, evidence=evidence,
                    evidence_directory=evidence_path.parent if evidence_path else None, decisions=decisions,
                )
                # Evidence identity and recorded rejection must be checked before generation.
                findings = [Finding(**item) for item in packet["findings"]]
            if out is not None:
                destination = out / identifier
                with artifact_directory(destination) as staging:
                    if operation == "build" and not failed(findings):
                        built = api.build(data, staging / "library", lib_name=identifier, check_kicad=check_kicad)
                        findings.extend(finding for finding in built.findings if finding not in findings)
                        if failed(built.findings):
                            # Keep the failure report but do not publish generated files that failed checks.
                            if (staging / "library").exists():
                                shutil.rmtree(staging / "library")
                        else:
                            files.extend(str(destination / Path(path).relative_to(staging)) for path in built.files)
                        if packet is not None:
                            packet["checks"]["kicad_load"] = (
                                "not_run" if not check_kicad or any(f.id == "kicad.unavailable" for f in built.findings)
                                else "failed" if any(f.id.startswith("kicad.") and f.status == FAIL for f in built.findings)
                                else "passed"
                            )
                            packet["checks"]["generated_artifacts"] = "failed" if failed(built.findings) else "passed"
                            if failed(built.findings):
                                packet["actions"].insert(0, {
                                    "action": "fix_generated_artifacts",
                                    "detail": "Generated files failed checks and were withheld; inspect the findings before rebuilding.",
                                })
                    if packet is not None:
                        packet["passed"] = not failed(findings)
                        packet["findings"] = [finding.to_dict() for finding in findings]
                        packet["artifacts"] = files[:]
                        write_json(staging / "handoff.json", packet)
                        write_json(staging / "review-input.json", packet["review_input"])
                        (staging / "REVIEW.md").write_text(review_markdown(packet), encoding="utf-8")
                        files.extend(str(destination / name) for name in ("handoff.json", "REVIEW.md", "review-input.json"))
                    write_json(staging / "partspec.json", data)
                    write_json(staging / "checks.json", api.summarize(findings, response_format=api.DETAILED))
                    files.extend(str(destination / name) for name in ("partspec.json", "checks.json"))
            item = api.summarize(findings, files)
            if packet is not None:
                item["actions"] = packet["actions"]
                item["generation"] = packet["generation"]
                item["checks"] = packet["checks"]
                item["review_counts"] = {key: packet["review"][key]
                                         for key in ("total", "accepted", "rejected", "pending", "needs_info")}
        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
            item = api.summarize([Finding("batch.item_failed", FAIL, f"job {identifier}: {exc}")])
            if out is not None and not (out / identifier).exists():
                with artifact_directory(out / identifier) as staging:
                    write_json(staging / "checks.json", item)
                item["files"] = [str(out / identifier / "checks.json")]
        items.append({"id": identifier, **item})
    report = {
        "schema": "partspec.batch-report/v1", "operation": operation,
        "passed": all(item["passed"] for item in items), "total": len(items),
        "succeeded": sum(item["passed"] for item in items),
        "failed_jobs": [item["id"] for item in items if not item["passed"]], "items": items,
    }
    if out is not None:
        write_json(out / "batch.json", report)
        report["report_file"] = str(out / "batch.json")
    return report
