"""Focused project invariants using in-memory inputs; no workflow, PDF or external processes."""

from copy import deepcopy
from pathlib import Path

import pytest

from kicad_partspec.artifacts import parse_json, relocate_paths
from kicad_partspec.decisions import content_hash
from kicad_partspec.project import _evidence_assets, _jobs
from kicad_partspec.project_reports import bom_csv, bom_rows, compare_reports, library_tables, open_items, project_html
from kicad_partspec.spec import load_spec


def test_json_ambiguity_and_nonfinite_dimensions_are_reported():
    for text in ('{"n":1,"n":2}', '{"n":NaN}', '{"n":Infinity}', '{"n":1e400}'):
        with pytest.raises(ValueError):
            parse_json(text)
    assert parse_json("null") is None
    assert parse_json('{"n":0.001}') == {"n": 0.001}
    raw = {"package": {"dimensions": {"height": {"nom": float("inf")}}}}
    spec, findings = load_spec(raw)
    assert spec is None
    assert any(f.path == "package.dimensions.height.nom" and "finite" in f.message for f in findings)


def test_check_scope_reduction_and_removed_tasks_are_not_fixes():
    previous = {"tasks": [{"id": "part:a", "inputs": {"a.json": {"sha256": "old"}},
                            "requested_checks": {"source_text": True},
                            "findings": [{"id": "prov.quote_not_found", "status": "fail", "path": "pins[0]"}]}]}
    current = deepcopy(previous)
    current["tasks"][0].update(inputs={"a.json": {"sha256": "new"}}, findings=[], requested_checks={"source_text": False})
    delta = compare_reports(current, previous)
    assert delta["changed_check_scope"] == ["part:a"]
    assert delta["resolved_failures"] == []
    assert delta["changed_inputs"] == {"part:a": ["a.json"]}
    current["tasks"][0]["requested_checks"]["source_text"] = True
    assert len(compare_reports(current, previous)["resolved_failures"]) == 1
    removed = compare_reports({"tasks": []}, previous)
    assert removed["removed_tasks"] == ["part:a"] and removed["resolved_failures"] == []


def test_bom_keeps_dnp_and_distinguishes_exact_specs_and_footprints():
    spec = {"mpn": "SYNTH", "manufacturer": "Invented", "package": {"family": "A"}}
    sibling = {**spec, "package": {"family": "B"}}
    circuit = {"parts": {"a": spec, "b": sibling}, "components": [
        {"ref": "U1", "kind": "part", "part": "a", "netlist_footprint": "Old:Package"},
        {"ref": "U2", "kind": "part", "part": "b"},
        {"ref": "C1", "kind": "capacitor", "capacitance_f": 22e-6, "populated": False},
    ]}
    catalog = {content_hash(spec): {"id": "a", "symbol": "parts/a/library/SYNTH.kicad_sym", "footprint": "parts/a/library/a.pretty/A.kicad_mod"}}
    rows = bom_rows(circuit, "supply", catalog)
    assert rows[0]["catalog_part"] == "a" and rows[1]["catalog_part"] == ""
    assert rows[0]["netlist_footprint"] == "Old:Package"
    assert rows[0]["generated_footprint"].endswith("/A.kicad_mod")
    assert rows[2]["populated"] is False and rows[2]["mpn"] == ""
    rows[0]["mpn"] = "=UNTRUSTED()"
    assert "'=UNTRUSTED()" in bom_csv(rows)
    assert rows[0]["mpn"] == "=UNTRUSTED()"  # JSON inventory preserves the original literal value


def test_library_tables_and_published_paths_remain_inside_the_bundle():
    tables = library_tables({"a": {"id": "chip", "symbol": "parts/chip/library/X.kicad_sym", "footprint": "parts/chip/library/chip.pretty/X.kicad_mod"}})
    assert '"${KIPRJMOD}/parts/chip/library/X.kicad_sym"' in tables["sym-lib-table"]
    assert '"${KIPRJMOD}/parts/chip/library/chip.pretty"' in tables["fp-lib-table"]
    with pytest.raises(ValueError):
        library_tables({"a": {"id": "chip", "symbol": "../other/X.kicad_sym"}})
    original = {"files": ["/tmp/stage/parts/a.json"], "source": "/tmp/stage-other/source.pdf", "quote": "an unchanged quotation"}
    moved = relocate_paths(original, Path("/tmp/stage"), Path("/project/output"))
    assert moved["files"] == ["/project/output/parts/a.json"]
    assert moved["source"] == original["source"] and moved["quote"] == original["quote"]
    assert original["files"] == ["/tmp/stage/parts/a.json"]


def test_project_manifest_and_evidence_do_not_silently_drop_bad_fields():
    with pytest.raises(ValueError):
        _jobs({"circuits": [{"id": "c", "import_path": "a.json", "circuit_path": "b.json"}]}, "circuits")
    with pytest.raises(ValueError):
        _jobs({"parts": [{"id": "p", "spec_path": "a.json", "decison_path": "b.json"}]}, "parts")
    with pytest.raises(ValueError):
        _evidence_assets({"schema": "partspec.evidence/v1", "pdf": "x.pdf", "page_count": 1, "pages": [{}]})


def test_project_report_preserves_failures_and_groups_inference_work():
    tasks = [{"id": "part:a", "state": "failed", "checks": {"source_text": "not_run"}, "report_path": "parts/a/REVIEW.md",
              "findings": [
                  {"id": "status.inferred", "status": "warn", "message": "inferred pin", "path": "pins[0]"},
                  {"id": "review.rejected", "status": "fail", "message": "<script>bad</script>", "path": "pins[0]"}],
              "actions": [{"action": "review_inferences", "fields": ["pins[0]"]}]}]
    items = open_items(tasks)
    assert len(items) == 2 and items[0]["severity"] == "failure"
    report = {"name": "<img src=x>", "state": "failed", "summary": {"tasks": 1, "failed_tasks": 1, "open_items": 2},
              "tasks": tasks, "open_items": items, "changes": None}
    page = project_html(report)
    assert "<img src=x>" not in page and "<script>bad</script>" not in page
    assert "&lt;script&gt;bad&lt;/script&gt;" in page and 'href="parts/a/REVIEW.md"' in page
