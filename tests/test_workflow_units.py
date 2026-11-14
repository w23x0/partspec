"""Small local checks of workflow invariants; no PDFs, models, subprocesses or KiCad."""

from copy import deepcopy

import pytest

from kicad_partspec.artifacts import artifact_directory, workspace_path
from kicad_partspec.circuit import check_circuit
from kicad_partspec.decisions import apply_decisions
from kicad_partspec.documents import index_pages, parse_pages, preview_candidates
from kicad_partspec.netlist import import_xml, passive_value
from kicad_partspec.review import review_packet
from kicad_partspec.verify import verify_spec


def _part():
    return {
        "mpn": "SYNTH-3", "manufacturer": "Invented",
        "datasheet": {"sha256": "0" * 64, "revision": "A"},
        "package": {"family": "SOT-23", "pin_count": 3, "dimensions": {}},
        "pins": [
            {"number": str(index), "name": name, "electrical_type": kind, "status": "inferred",
             "source": {"page": 1, "quote": f"{index} {name}"}}
            for index, name, kind in [(1, "OUT", "output"), (2, "IN", "input"), (3, "NC", "no_connect")]
        ],
    }


def _capacitors():
    return {
        "schema": "partspec.circuit/v1",
        "components": [
            {"ref": "C1", "kind": "capacitor", "capacitance_f": 10e-6, "tolerance": 0.2},
            {"ref": "C2", "kind": "capacitor", "capacitance_f": 15e-6, "tolerance": 0.1},
            {"ref": "C3", "kind": "capacitor", "capacitance_f": 100e-6, "tolerance": 0.1},
        ],
        "nets": [
            {"name": "VOUT", "pins": ["C1.1", "C2.1"]},
            {"name": "GND", "pins": ["C1.2", "C2.2", "C3.2"]},
            {"name": "OTHER", "pins": ["C3.1"]},
        ],
        "requirements": [{"id": "bulk", "kind": "capacitance_between", "nets": ["VOUT", "GND"], "min_f": 22e-6}],
    }


def test_textless_and_broken_pages_survive_inventory_and_preview_selection():
    texts = ["ordinary searchable body " * 10 for _ in range(40)]
    texts[7], texts[10], texts[20] = "", "\ufffd\x01", "LAND PATTERN " * 8
    pages = index_pages(texts, ["not present"])
    assert [page["page"] for page in pages] == list(range(1, 41))
    assert pages[7]["text_quality"] == "sparse"
    assert pages[10]["text_quality"] == "broken"
    assert {8, 11, 21} <= set(preview_candidates(pages, 24))
    assert all(page["preview"] is None for page in pages)  # selection has not rendered or inspected anything


def test_page_batches_are_bounded_and_use_pdf_indexes():
    assert parse_pages(" 1, 7-9, 8", maximum=10) == [1, 7, 8, 9]
    for expression in ("0", "9-7", "1-33", "11", "", "1,,2"):
        with pytest.raises(ValueError):
            parse_pages(expression, maximum=10)


def test_capacitance_uses_tolerance_and_only_directly_parallel_parts():
    plan = _capacitors()
    result = check_circuit(plan)
    assert not result["passed"]
    actual = result["requirements"][0]["actual"]
    assert actual["farads"] == pytest.approx(21.5e-6)
    assert actual["components"] == ["C1", "C2"]
    plan["requirements"][0]["basis"] = "nominal"
    result = check_circuit(plan)
    assert result["passed"]
    assert result["requirements"][0]["actual"]["farads"] == pytest.approx(25e-6)


def test_missing_tolerance_and_unsupported_requirements_cannot_pass():
    plan = _capacitors()
    del plan["components"][0]["tolerance"]
    plan["requirements"].append({"id": "unknown", "kind": "simulate_everything"})
    result = check_circuit(plan)
    assert not result["passed"]
    assert {f["id"] for f in result["findings"]} >= {"circuit.tolerance_required", "circuit.requirement_kind"}
    assert result["coverage"]["requirements_requested"] == 2
    assert result["coverage"]["requirements_evaluated"] == 0
    assert check_circuit({})["coverage"]["connectivity"] == "not_run"


def test_physical_pins_duplicate_wiring_no_connect_and_drivers_are_checked():
    plan = {
        "schema": "partspec.circuit/v1", "parts": {"chip": _part()},
        "components": [{"ref": ref, "kind": "part", "part": "chip"} for ref in ("U1", "U2")],
        "nets": [
            {"name": "A", "pins": ["U1.1", "U2.2"]},
            {"name": "B", "pins": ["U2.1", "U1.2"]},
        ],
    }
    assert check_circuit(plan)["passed"]  # NC pins are intentionally unwired
    plan["nets"][0]["pins"] += ["U1.OUT", "U1.3", "U2.1"]
    result = check_circuit(plan)
    assert not result["passed"]
    assert {f["id"] for f in result["findings"]} >= {
        "circuit.pin_missing", "circuit.no_connect", "circuit.driver_conflict", "circuit.pin_reused",
    }


def test_topology_and_voltage_constraints_expose_actual_values():
    plan = _capacitors()
    plan["components"][0]["rated_voltage_v"] = 6.3
    plan["requirements"] = [
        {"id": "joined", "kind": "same_net", "pins": ["C1.1", "C2.1"]},
        {"id": "separated", "kind": "separate_nets", "pins": ["C1.1", "C2.1"]},
        {"id": "rating", "kind": "voltage_rating", "ref": "C1", "min_v": 10},
    ]
    result = check_circuit(plan)
    assert [item["passed"] for item in result["requirements"]] == [True, False, False]
    assert result["requirements"][2]["actual"] == 6.3
    assert result["coverage"]["simulation"] == "not_run"


def test_handoff_preserves_unchecked_work_and_rejects_unrelated_evidence():
    data = _part()
    packet = review_packet(data, verify_spec(data))
    assert packet["passed"]
    assert packet["checks"]["source_text"] == "not_run"
    assert packet["checks"]["visual_binding"] == "requires_review"
    assert len(packet["inferred_fields"]) == 3
    assert packet["generation"]["footprint_possible"] is False
    evidence = {"schema": "partspec.evidence/v1", "sha256": "0" * 64, "page_count": 2,
                "pages": index_pages(["Pin table " * 10, ""])}
    packet = review_packet(data, verify_spec(data), evidence=evidence)
    assert any(action.get("pages") == [2] for action in packet["actions"])
    wrong = deepcopy(evidence)
    wrong["sha256"] = "a" * 64
    assert not review_packet(data, verify_spec(data), evidence=wrong)["passed"]
    evidence["pages"] = None
    assert not review_packet(data, verify_spec(data), evidence=evidence)["passed"]


def test_failed_artifacts_are_not_published_and_existing_work_is_preserved(tmp_path):
    destination = tmp_path / "packet"
    with pytest.raises(ValueError), artifact_directory(destination) as staging:
        (staging / "partial.txt").write_text("incomplete")
        raise ValueError("render failed")
    assert not destination.exists()
    with artifact_directory(destination) as staging:
        (staging / "original.txt").write_text("keep")
    with pytest.raises(FileExistsError), artifact_directory(destination):
        pytest.fail("must not overwrite an existing packet")
    assert (destination / "original.txt").read_text() == "keep"
    (tmp_path / "escape").symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(ValueError):
        workspace_path(tmp_path, "escape/outside.json")


def test_eda_labels_preserve_scale_and_reject_ambiguous_values():
    for label, kind, expected in [
        ("4k7", "resistor", 4700), ("4.7 kΩ", "resistor", 4700), ("0R", "resistor", 0),
        ("10m", "resistor", 0.01), ("10M", "resistor", 10e6),
        ("2u2", "capacitor", 2.2e-6), ("100nF", "capacitor", 100e-9), ("22µF", "capacitor", 22e-6),
    ]:
        assert passive_value(label, kind) == pytest.approx(expected)
    for label, kind in [("22", "capacitor"), ("10k 1%", "resistor"), ("1e999F", "capacitor")]:
        with pytest.raises(ValueError):
            passive_value(label, kind)


def test_xml_import_preserves_actual_pins_dnp_and_explicit_no_connects():
    xml = b'''<export version="E"><components>
      <comp ref="U1"><value>SYNTH-3</value><footprint>Project:Package</footprint></comp>
      <comp ref="C7"><value>22uF</value><property name="dnp"/></comp>
      </components><nets>
      <net name="OUT"><node ref="U1" pin="1"/><node ref="C7" pin="1"/></net>
      <net name="RETURN"><node ref="U1" pin="2"/><node ref="C7" pin="2"/></net>
      <net name="unused"><node ref="U1" pin="3" pintype="no_connect"/></net>
      </nets></export>'''
    bindings = {"U1": {"spec_path": "chip.json", "expected_footprint": "Project:Package"},
                "C7": {"kind": "capacitor", "tolerance": 0.2}}
    circuit, findings = import_xml(xml, bindings, {"U1": _part()})
    assert not findings and circuit is not None
    assert circuit["nets"][0] == {"name": "OUT", "pins": ["U1.1", "C7.1"]}
    assert len(circuit["nets"]) == 2 and "U1.3" in circuit["unconnected"]
    assert circuit["components"][1]["populated"] is False
    assert circuit["components"][1]["capacitance_f"] == pytest.approx(22e-6)
    assert circuit["parts"]["U1"]["mpn"] == "SYNTH-3"
    del bindings["C7"]
    circuit, findings = import_xml(xml, bindings, {"U1": _part()})
    assert circuit is None and any(f.id == "netlist.binding_missing" for f in findings)
    bindings["C7"] = {"kind": "capacitor"}
    bindings["U1"]["expected_footprint"] = "Project:Other"
    circuit, findings = import_xml(xml, bindings, {"U1": _part()})
    assert circuit is None and any(f.id == "netlist.footprint_mismatch" for f in findings)


def test_dnp_capacitors_do_not_satisfy_assembly_requirements():
    plan = _capacitors()
    plan["requirements"][0]["basis"] = "nominal"
    assert check_circuit(plan)["passed"]
    plan["components"][1]["populated"] = False
    result = check_circuit(plan)
    assert not result["passed"]
    assert result["requirements"][0]["actual"]["components"] == ["C1"]
    assert result["requirements"][0]["actual"]["farads"] == pytest.approx(10e-6)


def _decide(entries, verdict="accepted"):
    for index, entry in enumerate(entries):
        entry.update(verdict=verdict, reviewer_kind="human" if index == 0 else "model", reviewer="synthetic-test-actor",
                     reviewed_at="2026-11-15T12:00:00+08:00", note="Synthetic observation for an isolated unit check.")


def test_review_records_track_attribution_and_expire_after_changes():
    data = _part()
    original = deepcopy(data)
    template = review_packet(data, verify_spec(data))["review_input"]
    _decide(template["decisions"])
    packet = review_packet(data, verify_spec(data), decisions=template)
    assert packet["passed"] and packet["checks"]["visual_binding"] == "recorded_mixed_review"
    assert packet["checks"]["source_text"] == "not_run"
    assert packet["review"]["accepted"] == packet["review"]["total"]
    assert data == original and len(packet["inferred_fields"]) == 3
    assert any(action["action"] == "review_inferences" for action in packet["actions"])
    data["pins"][0]["name"] = "CHANGED"
    packet = review_packet(data, verify_spec(data), decisions=template)
    assert not packet["passed"] and packet["review"]["accepted"] == 0
    assert any(item["id"] == "review.stale_decisions" for item in packet["findings"])


def test_conflicting_and_rejected_decisions_cannot_clear_review_work():
    targets = {"part_binding": {"mpn": "SYNTH-3"}}
    state, _ = apply_decisions({}, targets)
    records = state["input"]
    _decide(records["decisions"])
    records["decisions"].append(deepcopy(records["decisions"][0]))
    state, findings = apply_decisions({}, targets, records)
    assert state["accepted"] == 0 and state["pending"] == 1
    assert any(f.id == "review.bad_decisions" for f in findings)
    records["decisions"].pop()
    records["decisions"][0]["verdict"] = "rejected"
    state, findings = apply_decisions({}, targets, records)
    assert state["state"] == "rejected" and any(f.id == "review.rejected" for f in findings)
