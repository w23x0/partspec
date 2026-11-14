"""Turn findings and provenance into a review queue and a portable handoff."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from kicad_partspec.artifacts import workspace_path
from kicad_partspec.decisions import apply_decisions
from kicad_partspec.findings import FAIL, Finding, failed
from kicad_partspec.gen.footprint import skip_reason
from kicad_partspec.spec import load_spec


def review_packet(
    data: Any, findings: list[Finding], *, source_checked: bool = False,
    evidence: Any = None, evidence_directory: Path | None = None,
    decisions: Any = None,
) -> dict[str, Any]:
    findings = list(findings)
    spec, structural_findings = load_spec(data)
    findings.extend(finding for finding in structural_findings if finding not in findings)
    pages: dict[int, list[dict[str, Any]]] = defaultdict(list)
    inferred: list[str] = []
    if spec is not None:
        items = [(f"pins[{i}]", pin, {"number": pin.number, "name": pin.name,
                  "electrical_type": pin.electrical_type}) for i, pin in enumerate(spec.pins)]
        items += [(f"package.dimensions.{name}", dim,
                   {key: value for key in ("min", "nom", "max") if (value := getattr(dim, key)) is not None})
                  for name, dim in spec.package.dimensions.items()]
        for path, item, value in items:
            if item.status == "inferred":
                inferred.append(path)
            if item.source is not None:
                pages[item.source.page].append({
                    "path": path, "value": value, "status": item.status, "quote": item.source.quote,
                    "review": "Check the dimension's extension lines and metal/mask boundary."
                    if path.startswith("package.") else "Check the requested part/package and pin-number/name pairing.",
                })
    navigation: dict[int, dict[str, Any]] = {}
    if evidence is not None:
        if not isinstance(evidence, dict) or evidence.get("schema") != "partspec.evidence/v1":
            findings.append(Finding("review.bad_evidence", FAIL, "use a manifest.json produced by prepare"))
        elif spec is not None and evidence.get("sha256") != spec.datasheet.sha256:
            findings.append(Finding(
                "review.evidence_mismatch", FAIL,
                "the page inventory belongs to different PDF bytes; use evidence matching datasheet.sha256 and keep rebuilds explicit",
                path="datasheet.sha256", expected=spec.datasheet.sha256, actual=evidence.get("sha256"),
            ))
        else:
            inventory = evidence.get("pages")
            count = evidence.get("page_count")
            if (type(count) is not int or count < 1 or not isinstance(inventory, list) or len(inventory) != count
                    or any(not isinstance(page, dict) or type(page.get("page")) is not int
                           or page["page"] != index
                           or page.get("text_quality") not in ("searchable", "sparse", "broken")
                           for index, page in enumerate(inventory, 1))):
                findings.append(Finding("review.bad_evidence", FAIL,
                                        "evidence must contain one ordered page entry per PDF page; run prepare again"))
            else:
                for page in inventory:
                    entry = dict(page)
                    preview = entry.get("preview")
                    if preview is not None:
                        try:
                            if not isinstance(preview, str) or not preview or Path(preview).is_absolute():
                                raise ValueError("preview must be a relative path inside the evidence directory")
                            location = workspace_path(evidence_directory or Path.cwd(), preview)
                            entry["preview"] = str(location) if evidence_directory is not None else preview
                        except (OSError, ValueError, RuntimeError) as exc:
                            findings.append(Finding("review.bad_evidence", FAIL, str(exc)))
                            entry["preview"] = None
                    navigation[page["page"]] = entry
                for number in pages:
                    if number not in navigation:
                        findings.append(Finding("review.page_out_of_range", FAIL,
                                                f"cited PDF page {number} is outside the evidence inventory (1..{count})"))
    unseen = [number for number, page in navigation.items()
              if page.get("text_quality") != "searchable" and number not in pages]
    targets: dict[str, dict[str, Any]] = {}
    if spec is not None:
        targets["part_binding"] = {
            "mpn": spec.mpn, "manufacturer": spec.manufacturer, "package": spec.package.family,
            "pin_count": spec.package.pin_count,
            "review": "Check the requested orderable part, package and drawing revision against the datasheet.",
        }
        for number, fields in pages.items():
            targets.update({item["path"]: {"page": number, **item} for item in fields})
        for number in unseen:
            targets[f"page:{number}"] = {
                "page": number, "text_quality": navigation[number]["text_quality"],
                "review": "Inspect the page for relevant evidence omitted from the PartSpec; record what you found.",
            }
    review_state, decision_findings = apply_decisions(data, targets, decisions)
    findings.extend(decision_findings)
    remaining = {item["target"] for item in review_state["items"] if item["verdict"] != "accepted"}
    human_reviewed = {item["target"] for item in review_state["items"]
                      if item["verdict"] == "accepted" and item["reviewer_kind"] == "human"}
    reason = skip_reason(spec) if spec is not None else "fix the PartSpec structure first"
    failures = [finding.to_dict() for finding in findings if finding.status == FAIL]
    actions: list[dict[str, Any]] = []
    if failures:
        actions.append({"action": "fix_findings", "count": len(failures), "details": failures})
    if not source_checked:
        actions.append({"action": "check_source_text", "detail": "validate with the exact datasheet PDF to check quotes"})
    pending_inferences = [path for path in inferred if path not in human_reviewed]
    if pending_inferences:
        actions.append({"action": "review_inferences", "fields": pending_inferences})
    if reason:
        actions.append({"action": "resolve_footprint", "detail": reason})
    if "part_binding" in remaining:
        actions.append({"action": "inspect_part_binding", "detail": targets["part_binding"]["review"]})
    pending_pages = [number for number, fields in pages.items() if any(item["path"] in remaining for item in fields)]
    if pending_pages:
        actions.append({"action": "inspect_visual_bindings", "pages": sorted(pending_pages),
                        "detail": "Text matching cannot prove that a value belongs to this pin, dimension or package."})
    pending_unseen = [number for number in unseen if f"page:{number}" in remaining]
    if pending_unseen:
        actions.append({"action": "inspect_uncited_visual_pages", "pages": sorted(pending_unseen),
                        "detail": "These sparse or broken-text pages may contain omitted drawings; previewing is not review."})
    source_failed = any(f.id.startswith("prov.") and f.status == FAIL for f in findings)
    source_state = "not_run"
    if source_checked:
        source_state = "blocked" if spec is None else "failed" if source_failed else "passed"
        if source_state == "passed" and any(f.id == "prov.datasheet_rebuilt" for f in findings):
            source_state = "passed_on_rebuilt_pdf"
    return {
        "schema": "partspec.handoff/v1", "passed": not failed(findings),
        "mpn": spec.mpn if spec else None,
        "datasheet": data.get("datasheet") if isinstance(data, dict) else None,
        "checks": {
            "input_checks": "failed" if failures else "passed",
            "source_text": source_state,
            "visual_binding": review_state["state"], "kicad_load": "not_run", "electrical_function": "not_run",
        },
        "generation": {"symbol_possible": not bool(failures),
                       "footprint_possible": not failures and reason is None, "footprint_blocker": reason},
        "actions": actions, "inferred_fields": inferred,
        "review": {key: value for key, value in review_state.items() if key != "input"},
        "review_input": review_state["input"],
        "evidence_directory": str(evidence_directory) if evidence_directory else None,
        "pages": [{"page": number, "fields": fields,
                   "preview": navigation.get(number, {}).get("preview"),
                   "text_quality": navigation.get(number, {}).get("text_quality", "unknown")}
                  for number, fields in sorted(pages.items())],
        "findings": [finding.to_dict() for finding in findings],
    }


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ").replace("<", "&lt;")


def review_markdown(packet: dict[str, Any]) -> str:
    lines = [f"# Review: {_cell(packet.get('mpn') or 'invalid PartSpec')}", "",
             "This packet records checks performed and work still required. File generation does not establish circuit performance.", "",
             "| Check | State |", "|---|---|"]
    lines += [f"| {_cell(key)} | {_cell(value)} |" for key, value in packet["checks"].items()]
    lines += ["", "## Next actions", ""]
    for action in packet["actions"]:
        detail = action.get("detail") or action.get("fields") or f'{action.get("count", 0)} findings'
        if action.get("pages"):
            detail = f'{detail} PDF pages: {action["pages"]}'
        lines.append(f'- **{_cell(action["action"])}**: {_cell(detail)}')
    for finding in packet["findings"]:
        if finding["status"] == FAIL:
            lines.append(f'- `{_cell(finding["id"])}`: {_cell(finding["message"])}')
    if packet["review"]["items"]:
        lines += ["", "## Recorded review", "",
                  "Entries are attributed records supplied by the reviewer; they do not change extraction status or run checks.", "",
                  "| Target | Verdict | Reviewer kind | Reviewer | Reviewed at | Note |", "|---|---|---|---|---|---|"]
        for item in packet["review"]["items"]:
            lines.append("| " + " | ".join(_cell(item[key]) for key in ("target", "verdict", "reviewer_kind", "reviewer", "reviewed_at", "note")) + " |")
    for page in packet["pages"]:
        lines += ["", f'## PDF page {page["page"]}', ""]
        if page.get("preview"):
            lines += [f'Preview: `{_cell(page["preview"])}`', ""]
        lines += ["| Field | Value | Status | Evidence | Review |", "|---|---|---|---|---|"]
        for item in page["fields"]:
            lines.append("| " + " | ".join(_cell(item[key]) for key in ("path", "value", "status", "quote", "review")) + " |")
    return "\n".join(lines) + "\n"
