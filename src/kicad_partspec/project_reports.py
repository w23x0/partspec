"""Project summaries, change reports and library/BOM exports, without running tools."""

from __future__ import annotations

import csv
import html
import io
from pathlib import Path
from typing import Any
from urllib.parse import quote

from kicad_partspec.decisions import content_hash
from kicad_partspec.sexpr import Atom, write_sexpr


def open_items(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = []
    for task in tasks:
        actions = task.get("actions", [])
        for finding in task.get("findings", []):
            if finding.get("id") == "status.inferred":
                continue  # part-review actions or uncatalogued-part findings retain this work as a group
            if finding.get("id") == "footprint.skipped" and any(action["action"] == "resolve_footprint" for action in actions):
                continue
            if finding.get("status") in ("fail", "warn"):
                items.append({"task": task["id"], "severity": "failure" if finding["status"] == "fail" else "review",
                              "code": finding["id"], "message": finding["message"], "path": finding.get("path", "")})
        for action in actions:
            if action["action"] == "fix_findings":
                continue  # individual failures above carry the actionable detail
            message = action.get("detail") or ", ".join(action.get("fields", [])) or "Review the associated report."
            if action.get("pages"):
                message += f' PDF pages: {action["pages"]}.'
            items.append({"task": task["id"], "severity": "review", "code": action["action"], "message": message,
                          "path": ""})
    ordered = sorted(items, key=lambda item: (item["severity"] != "failure", item["task"], item["code"], item["path"]))
    unique = {}
    for item in ordered:
        unique.setdefault((item["task"], item["message"]), item)
    return list(unique.values())


def compare_reports(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    before = {task["id"]: task for task in previous["tasks"]}
    after = {task["id"]: task for task in current["tasks"]}
    delta: dict[str, Any] = {
        "added_tasks": sorted(after.keys() - before.keys()), "removed_tasks": sorted(before.keys() - after.keys()),
        "changed_inputs": {}, "changed_check_scope": [], "new_failures": [], "resolved_failures": [],
    }
    for identifier, task in after.items():
        old = before.get(identifier)
        if old is not None:
            old_inputs, new_inputs = old.get("inputs", {}), task.get("inputs", {})
            changed = sorted(key for key in old_inputs.keys() | new_inputs.keys() if old_inputs.get(key) != new_inputs.get(key))
            if changed:
                delta["changed_inputs"][identifier] = changed
            if old.get("requested_checks") != task.get("requested_checks"):
                delta["changed_check_scope"].append(identifier)
                continue  # stopping a check is not a fix

        def failures(item: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
            return {(f["id"], f.get("path", "")): f for f in item.get("findings", []) if f.get("status") == "fail"}

        old_failures, new_failures = failures(old or {}), failures(task)
        delta["new_failures"].extend({"task": identifier, **new_failures[key]} for key in sorted(new_failures.keys() - old_failures.keys()))
        delta["resolved_failures"].extend({"task": identifier, **old_failures[key]} for key in sorted(old_failures.keys() - new_failures.keys()))
    return delta


def bom_rows(circuit: dict[str, Any], circuit_id: str, catalog: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for component in circuit["components"]:
        kind = component["kind"]
        spec = circuit.get("parts", {}).get(component.get("part"), {}) if kind == "part" else {}
        digest = content_hash(spec) if spec else ""
        match = catalog.get(digest, {})
        rows.append({
            "circuit": circuit_id, "ref": component["ref"], "populated": component.get("populated", True),
            "kind": kind, "mpn": spec.get("mpn", ""), "manufacturer": spec.get("manufacturer", ""),
            "value_si": component.get("capacitance_f", component.get("resistance_ohm", "")),
            "unit": "F" if kind == "capacitor" else "ohm" if kind == "resistor" else "",
            "tolerance": component.get("tolerance", ""), "rated_voltage_v": component.get("rated_voltage_v", ""),
            "netlist_footprint": component.get("netlist_footprint", ""), "catalog_part": match.get("id", ""),
            "generated_symbol": match.get("symbol", ""), "generated_footprint": match.get("footprint", ""),
            "spec_sha256": digest,
        })
    return rows


def bom_csv(rows: list[dict[str, Any]]) -> str:
    columns = ["circuit", "ref", "populated", "kind", "mpn", "manufacturer", "value_si", "unit", "tolerance",
               "rated_voltage_v", "netlist_footprint", "catalog_part", "generated_symbol", "generated_footprint", "spec_sha256"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        # JSON retains literal values; CSV cells must not execute spreadsheet formulas.
        writer.writerow({key: "'" + str(value) if str(value).startswith(("=", "+", "-", "@", "\t", "\r")) else value
                         for key, value in row.items()})
    return stream.getvalue()


def library_tables(catalog: dict[str, dict[str, Any]]) -> dict[str, str]:
    symbols: list[Any] = [Atom("sym_lib_table")]
    footprints: list[Any] = [Atom("fp_lib_table")]
    for part in catalog.values():
        for key, tree in (("symbol", symbols), ("footprint", footprints)):
            value = part.get(key)
            if not value:
                continue
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("generated library paths must be relative to the project bundle")
            location = path if key == "symbol" else path.parent
            tree.append([Atom("lib"), [Atom("name"), part["id"]], [Atom("type"), "KiCad"],
                         [Atom("uri"), "${KIPRJMOD}/" + location.as_posix()], [Atom("options"), ""],
                         [Atom("descr"), "Generated from a PartSpec; see the project report for review status."]])
    return {name: write_sexpr(tree) for name, tree in (("sym-lib-table", symbols), ("fp-lib-table", footprints)) if len(tree) > 1}


def project_markdown(report: dict[str, Any]) -> str:
    def safe(value: str) -> str:
        return html.escape(value).replace("\n", " ").replace("\r", " ").replace("|", "\\|")

    lines = [f'# {safe(report["name"])}', "", f'State: **{report["state"]}**. {report["summary"]["failed_tasks"]} task(s) failed; '
             f'{report["summary"]["open_items"]} item(s) need attention.', "",
             "Open index.html for searchable tasks and actions. These results describe the requested checks, not circuit performance.", "",
             "| Task | State | Report |", "|---|---|---|"]
    for task in report["tasks"]:
        lines.append(f'| {task["id"]} | {task["state"]} | [{task["report_path"]}]({task["report_path"]}) |')
    lines += ["", "## Next actions", ""]
    for item in report["open_items"]:
        message = safe(item["message"])
        lines.append(f'- **{item["task"]} / {item["severity"]}** — {message}')
    if not report["open_items"]:
        lines.append("No outstanding items were reported by the requested checks.")
    if report.get("changes") is not None:
        change = report["changes"]
        lines += ["", "## Changes since the baseline", "",
                  f'- New failures: {len(change["new_failures"])}; resolved failures: {len(change["resolved_failures"])}.',
                  f'- Changed inputs: {len(change["changed_inputs"])} task(s); changed check scope: {change["changed_check_scope"]}.',
                  "Changed check scope is not counted as a resolved failure. See project.json for file names and findings."]
    lines += ["", "## Files", "", "- project.json: complete report and input fingerprints.",
              "- project-input.json: the original project manifest.", "- bom.json / bom.csv: one row per component; DNP is preserved.",
              "- parts/ and circuits/: individual results, including failures.",
              "- sym-lib-table / fp-lib-table: generated only when corresponding library files exist.",
              "", "Library-table paths use ${KIPRJMOD}. Copy the bundle together with its tables into the KiCad project directory;",
              "merge table entries if that project already has library tables. No existing KiCad project was modified.", ""]
    return "\n".join(lines)


def project_html(report: dict[str, Any]) -> str:
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    def link(path: str, label: str) -> str:
        return f'<a href="{quote(path, safe="/")}">{esc(label)}</a>'

    task_rows = []
    for task in report["tasks"]:
        checks = ", ".join(f"{key}: {value}" for key, value in task.get("checks", {}).items())
        links = link(task["report_path"], "Open report")
        if task.get("evidence_path"):
            links += " · " + link(task["evidence_path"], "Evidence pages")
        task_rows.append(f'<tr data-row data-state="{esc(task["state"])}"><td>{esc(task["id"])}</td>'
                         f'<td>{esc(task["state"])}</td><td>{esc(checks)}</td><td>{links}</td></tr>')
    action_rows = [f'<li data-row data-state="{"failed" if item["severity"] == "failure" else "needs_review"}">'
                   f'<strong>{esc(item["task"])}</strong> · {esc(item["code"])}<p>{esc(item["message"])}</p>'
                   f'<small>{esc(item["path"])}</small></li>' for item in report["open_items"]]
    change = report.get("changes")
    changes = (f'<p>Baseline: {len(change["new_failures"])} new failure(s), {len(change["resolved_failures"])} resolved; '
               f'{len(change["changed_check_scope"])} task(s) changed check scope.</p>' if change is not None else "")
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(report["name"])} — PartSpec</title><style>'
        'body{font:16px/1.55 system-ui,sans-serif;color:#172738;background:#f4f6f9;max-width:1200px;margin:auto;padding:28px}'
        'header,section{background:white;padding:24px;margin-bottom:20px;border:1px solid #d9e0e8;border-radius:10px}'
        'h1{margin:0 0 8px}h2{margin-top:0}a{color:#155c9b}table{border-collapse:collapse;width:100%}'
        'td,th{text-align:left;padding:10px;border-bottom:1px solid #d9e0e8;vertical-align:top;overflow-wrap:anywhere}'
        'li{padding:12px 0;border-bottom:1px solid #e3e7ec}li p{margin:4px 0}small{color:#526578}'
        'input,select{font:inherit;padding:8px;border:1px solid #aab8c7;border-radius:5px}input{max-width:100%;width:360px}'
        '.scroll{overflow:auto}[hidden]{display:none!important}nav{display:flex;gap:20px;flex-wrap:wrap}</style></head><body>'
        f'<header><h1>{esc(report["name"])}</h1><p><strong>{esc(report["state"])}</strong> · '
        f'{report["summary"]["tasks"]} tasks · {report["summary"]["failed_tasks"]} failed · '
        f'{report["summary"]["open_items"]} open items</p>'
        '<p>Results cover the requested checks. Recorded review, source text, generated files and circuit requirements have separate states.</p>'
        f'{changes}<nav>{link("project.json", "Full JSON report")}{link("bom.csv", "BOM CSV")}'
        f'{link("bom.json", "BOM and omissions")}{link("PROJECT.md", "Handoff")}</nav></header>'
        '<section><label>Search <input id="query" type="search" placeholder="Part, pin, net or finding"></label> '
        '<label>State <select id="state"><option value="">All</option><option value="failed">Failures</option>'
        '<option value="needs_review">Needs review</option><option value="checks_passed">Checks passed</option></select></label></section>'
        '<section><h2>Tasks</h2><div class="scroll"><table><thead><tr><th>Task</th><th>State</th><th>Checks</th><th>Result</th>'
        f'</tr></thead><tbody>{"".join(task_rows)}</tbody></table></div></section><section><h2>Next actions</h2>'
        f'<ul>{"".join(action_rows)}</ul></section>'
        '<script>const query=document.querySelector("#query"),state=document.querySelector("#state");'
        'function filter(){for(const row of document.querySelectorAll("[data-row]")){'
        'row.hidden=!(row.textContent.toLowerCase().includes(query.value.toLowerCase())&&(!state.value||row.dataset.state===state.value));}}'
        'query.addEventListener("input",filter);state.addEventListener("change",filter);</script></body></html>'
    )
