"""Spec-layer checker properties, exercised on one synthetic document.

The base document below is SYNTHETIC (an invented 4-pin part) and exists only to
test the checkers; real datasheet-derived cases live in ``evals/cases``. The
planted-error table that used to live here moved to ``tests/test_rules.py``,
where every planted case is named after the rule (SCH-*) it defends, so the
audit in ``scripts/audit.py`` can attribute failures per rule.
"""

import copy
import json
import os
from pathlib import Path

import pytest

from kicad_partspec.cli import main
from kicad_partspec.verify import verify_spec
from kicad_partspec.verify.quotes import (
    check_quotes,
    document_number,
    first_page,
    page_texts,
    resolve_datasheet,
    sha256_of,
)

DATASHEETS = os.environ.get("PARTSPEC_DATASHEETS")
CASES = Path(__file__).resolve().parent.parent / "evals" / "cases"


def gold_datasheet(case):
    return json.loads((CASES / case / "spec.gold.json").read_text(encoding="utf-8"))["datasheet"]


def check_quotes_gold(case, datasheets):
    data = json.loads((CASES / case / "spec.gold.json").read_text(encoding="utf-8"))
    pdf, _ = resolve_datasheet(data["datasheet"], datasheets)
    return check_quotes(data, page_texts(pdf))


def src(page=1, quote="Table 1"):
    return {"page": page, "quote": quote}


BASE = {
    "mpn": "SYNTH-4",
    "manufacturer": "Synthetic",
    "datasheet": {"sha256": "0" * 64, "revision": "A"},
    "package": {
        "family": "SOT",
        "pin_count": 4,
        "exposed_pad": False,
        "dimensions": {"pitch": {"min": 0.9, "nom": 0.95, "max": 1.0, "source": src(2, "e 0.95")}},
    },
    "pins": [
        {"number": "1", "name": "VIN", "electrical_type": "power_in", "source": src()},
        {"number": "2", "name": "GND", "electrical_type": "power_in", "source": src()},
        {"number": "3", "name": "EN", "electrical_type": "input", "source": src()},
        {"number": "4", "name": "VOUT", "electrical_type": "power_out", "source": src()},
    ],
}


def mutated(mutate):
    data = copy.deepcopy(BASE)
    mutate(data)
    return data


def failing_ids(data, status="fail"):
    return {item.id for item in verify_spec(data) if item.status == status}


def test_all_structural_errors_reported_in_one_pass():
    data = mutated(lambda d: (d.pop("mpn"), d["package"].update(pin_count=0), d["pins"][0].pop("name")))
    paths = {item.path for item in verify_spec(data) if item.id == "schema.invalid"}
    assert {".mpn", "package.pin_count", "pins[0].name"} <= paths


def test_findings_carry_actionable_messages():
    for item in verify_spec(mutated(lambda d: d["pins"].pop())):
        assert item.message and item.path


def test_cli_exit_codes(tmp_path, capsys):
    good = tmp_path / "good.json"
    good.write_text(json.dumps(BASE))
    assert main(["validate", str(good)]) == 0
    assert json.loads(capsys.readouterr().out)["passed"] is True

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(mutated(lambda d: d["pins"].pop())))
    assert main(["validate", str(bad)]) == 1
    assert json.loads(capsys.readouterr().out)["passed"] is False

    broken = tmp_path / "broken.json"
    broken.write_text("{not json")
    assert main(["validate", str(broken)]) == 2
    assert main(["validate", str(tmp_path / "missing.json")]) == 2


# --- datasheet resolution: hash first, same-revision rebuild as a named fallback ---------------------


@pytest.mark.parametrize(
    "revision, expected",
    [
        ("SLOS068AB (Rev. AB, October 2024)", "SLOS068AB"),
        ("DS20001203U (Revision U, 11/2013)", "DS20001203U"),
        ("SLVSAG7F (Rev. F, November 2021); RGT0016C drawing dated 07/2025", "SLVSAG7F"),
        # no literature number: the RP2040 sheet names a build, Nexperia's a date
        ("build-date 2025-02-20, build-version 3184e62-clean (no revision letter printed)", None),
        ("Rev. 12 — 20 March 2024", None),
    ],
)
def test_document_number_reads_the_literature_number(revision, expected):
    assert document_number(revision) == expected


@pytest.mark.skipif(not DATASHEETS, reason="PARTSPEC_DATASHEETS is not set; the PDFs live outside the repo")
def test_a_same_revision_rebuild_resolves_by_its_document_number():
    """The lm358 gold cites bytes no Wayback snapshot holds; the vendor re-issued the same
    revision as a new file, and the fallback must name that, not pretend the hash matched."""
    directory = Path(DATASHEETS)
    sheet = gold_datasheet("lm358_soic8")
    pdf, mode = resolve_datasheet(sheet, directory)
    assert mode == "rebuilt"
    assert pdf is not None
    assert sha256_of(pdf) != sheet["sha256"]
    assert "SLOS068AB" in first_page(pdf)
    assert not check_quotes_gold("lm358_soic8", directory)
