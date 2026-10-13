import json
import os
import shutil
from pathlib import Path

import pytest

from kicad_partspec.findings import WARN, failed
from kicad_partspec.verify import verify_spec
from kicad_partspec.verify.quotes import (
    check_quotes,
    document_number,
    first_page,
    normalize,
    page_texts,
    resolve_datasheet,
    suggest_quote,
)

CASES = Path(__file__).resolve().parent.parent / "evals" / "cases"
GOLD = sorted(CASES.glob("*/spec.gold.json"))
DATASHEETS = os.environ.get("PARTSPEC_DATASHEETS")


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_gold_cases_exist():
    assert len(GOLD) >= 3


@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_gold_passes_spec_layer(path):
    findings = verify_spec(_load(path))
    assert not failed(findings), [item.to_dict() for item in findings if item.status == "fail"]


@pytest.mark.skipif(not DATASHEETS, reason="set PARTSPEC_DATASHEETS to a directory holding the datasheet PDFs")
@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext not installed")
@pytest.mark.parametrize("path", GOLD, ids=[p.parent.name for p in GOLD])
def test_gold_quotes_match_datasheet(path):
    data = _load(path)
    pdf, mode = resolve_datasheet(data["datasheet"], Path(DATASHEETS))
    assert pdf is not None, "no PDF in PARTSPEC_DATASHEETS matches datasheet.sha256 or its revision"
    if mode == "rebuilt":
        # the fallback is a named substitution, never a silent one: same document number on page 1
        assert document_number(data["datasheet"]["revision"]) in first_page(pdf)
    findings = check_quotes(data, page_texts(pdf))
    assert not findings, [item.to_dict() for item in findings]


# --- api.validate with the datasheet PDF -----------------------------------------------------------


def test_normalize_collapses_whitespace():
    assert normalize("a \n\t b") == "a b"


# --- api.validate with the datasheet PDF -----------------------------------------------------------


@pytest.mark.skipif(not DATASHEETS, reason="set PARTSPEC_DATASHEETS to a directory holding the datasheet PDFs")
@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="pdftotext not installed")
class TestValidateAgainstThePdf:
    @staticmethod
    def _case():
        path = CASES / "lm358_soic8" / "spec.gold.json"
        data = _load(path)
        pdf, mode = resolve_datasheet(data["datasheet"], Path(DATASHEETS))
        assert pdf is not None and mode in ("sha", "rebuilt")
        return data, pdf

    def test_gold_passes_with_the_pdf(self):
        from kicad_partspec import api

        data, pdf = self._case()
        assert not failed(api.validate(data, pdf))

    def test_a_wrong_sha_still_fails_when_the_file_is_not_the_revision(self):
        """A vendor rebuild degrades to a named warning; a genuinely wrong file still fails.
        The revision is blanked here so the scenario is the wrong file, not the rebuild."""
        from kicad_partspec import api

        data, pdf = self._case()
        data["datasheet"]["sha256"] = "0" * 64
        data["datasheet"]["revision"] = "unrelated document"
        findings = [item for item in api.validate(data, pdf) if item.id == "prov.datasheet_sha_mismatch"]
        assert findings and findings[0].expected in findings[0].message

    def test_a_same_revision_rebuild_warns_instead_of_failing(self):
        """TI re-issued SLOS068AB as new bytes: quotes still checked, the spec's sha256 kept,
        and the finding says not to rewrite it (what the old FAIL message told you to do)."""
        from kicad_partspec import api

        data, pdf = self._case()
        (finding,) = [item for item in api.validate(data, pdf) if item.id == "prov.datasheet_rebuilt"]
        assert finding.status == WARN and "Do not rewrite" in finding.message

    def test_an_invented_quote_is_caught(self):
        from kicad_partspec import api

        data, pdf = self._case()
        data["pins"][0]["source"]["quote"] = "OUT1 wired to the moon"
        assert "prov.quote_not_found" in {item.id for item in api.validate(data, pdf)}

    def test_a_missing_pdf_is_reported_not_raised(self):
        from kicad_partspec import api

        data, _ = self._case()
        assert "prov.datasheet_unreadable" in {item.id for item in api.validate(data, Path("/nonexistent.pdf"))}


# --- quote suggestions --------------------------------------------------------------------------------


def _doc(page, quote):
    return {"pins": [{"source": {"page": page, "quote": quote}}], "package": {"dimensions": {}}}


def test_a_failed_quote_gets_the_real_layout_order_as_advice():
    pages = ["1.0        C\n0.8\n  SEATING PLANE\n0.05     0.08\n0.00"]
    (finding,) = check_quotes(_doc(1, "1.0 0.8"), pages)
    assert finding.expected == "1.0 C 0.8" and "1.0 C 0.8" in finding.message
    # the suggestion itself passes
    assert check_quotes(_doc(1, finding.expected), pages) == []
    (finding,) = check_quotes(_doc(1, "0.05 0.00"), pages)
    assert finding.expected == "0.05 0.08 0.00"


def test_no_suggestion_when_a_token_is_not_on_the_page_or_too_far_apart():
    pages = ["1.0 C 0.8 and then a very long stretch of unrelated text before we finally see 9.9 here"]
    (missing,) = check_quotes(_doc(1, "1.0 7.7"), pages)
    assert missing.expected is None and "pdftotext -layout" in missing.message
    (far,) = check_quotes(_doc(1, "1.0 9.9"), pages)
    assert far.expected is None


def test_the_shortest_stretch_wins():
    page = "a x x b   a y b"  # 'a ... b' occurs twice; the second stretch is shorter
    assert suggest_quote("a b", page) == "a y b"
    assert suggest_quote("a b", "a b") is None  # already matches, nothing to suggest
