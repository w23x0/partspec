"""Spec-layer checks: internal consistency of a loaded PartSpec.

Each check returns findings and never raises; ``message`` tells the agent what
to change.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable

from kicad_partspec.findings import FAIL, WARN, Finding
from kicad_partspec.spec.model import ELECTRICAL_TYPES, STATUSES, PartSpec, Source


def _source_problem(source: Source | None) -> str | None:
    if source is None:
        return "has no source"
    if source.page < 1:
        return "has source.page < 1"
    if not source.quote.strip():
        return "has an empty source.quote"
    return None


def check_provenance(spec: PartSpec) -> list[Finding]:
    """Every pin and dimension must cite a datasheet page and a quote."""
    findings: list[Finding] = []
    items = [(f"pins[{i}]", pin.source) for i, pin in enumerate(spec.pins)]
    items += [(f"package.dimensions.{name}", dim.source) for name, dim in spec.package.dimensions.items()]
    for path, source in items:
        problem = _source_problem(source)
        if problem:
            findings.append(
                Finding(
                    "prov.missing",
                    FAIL,
                    f"{path} {problem}; cite the datasheet page number and quote the table row or figure text.",
                    path=path,
                )
            )
    return findings


def check_pin_count(spec: PartSpec) -> list[Finding]:
    expected = spec.package.pin_count + (1 if spec.package.exposed_pad else 0)
    if len(spec.pins) == expected:
        return []
    detail = " (package.pin_count plus one exposed pad)" if spec.package.exposed_pad else ""
    return [
        Finding(
            "pins.count_mismatch",
            FAIL,
            f"pins has {len(spec.pins)} entries but the package needs {expected}{detail}; "
            "add the missing pins or correct package.pin_count.",
            path="pins",
            expected=expected,
            actual=len(spec.pins),
        )
    ]


def check_pin_numbers_unique(spec: PartSpec) -> list[Finding]:
    counts = Counter(pin.number for pin in spec.pins)
    return [
        Finding(
            "pins.duplicate_number",
            FAIL,
            f"pin number {number!r} appears {count} times; every physical pin needs a unique number.",
            path="pins",
            actual=count,
        )
        for number, count in sorted(counts.items())
        if count > 1
    ]


def check_electrical_types(spec: PartSpec) -> list[Finding]:
    return [
        Finding(
            "pins.bad_type",
            FAIL,
            f"pins[{i}].electrical_type {pin.electrical_type!r} is not a KiCad pin type; "
            f"use one of: {', '.join(ELECTRICAL_TYPES)}.",
            path=f"pins[{i}].electrical_type",
            expected=list(ELECTRICAL_TYPES),
            actual=pin.electrical_type,
        )
        for i, pin in enumerate(spec.pins)
        if pin.electrical_type not in ELECTRICAL_TYPES
    ]


def check_dimension_order(spec: PartSpec) -> list[Finding]:
    findings: list[Finding] = []
    for name, dim in spec.package.dimensions.items():
        path = f"package.dimensions.{name}"
        values = [
            (label, value)
            for label, value in (("min", dim.min), ("nom", dim.nom), ("max", dim.max))
            if value is not None
        ]
        if not values:
            findings.append(
                Finding("dim.empty", FAIL, f"{path} has no min, nom or max; provide at least one value.", path=path)
            )
            continue
        # A minimum of 0 is legitimate (e.g. a standoff that can sit on the board);
        # nominal and maximum values must be strictly positive.
        if any(value < 0 or (value == 0 and label != "min") for label, value in values):
            findings.append(
                Finding(
                    "dim.non_positive",
                    FAIL,
                    f"{path} has a negative value, or a nom/max of 0; dimensions are in mm, min may be 0.",
                    path=path,
                )
            )
        numbers = [value for _, value in values]
        if numbers != sorted(numbers):
            findings.append(
                Finding(
                    "dim.order",
                    FAIL,
                    f"{path} must satisfy min <= nom <= max; re-read the datasheet table for this dimension.",
                    path=path,
                    actual={label: value for label, value in values},
                )
            )
    return findings


def check_statuses(spec: PartSpec) -> list[Finding]:
    findings: list[Finding] = []
    items = [(f"pins[{i}]", pin.status) for i, pin in enumerate(spec.pins)]
    items += [(f"package.dimensions.{name}", dim.status) for name, dim in spec.package.dimensions.items()]
    for path, status in items:
        if status not in STATUSES:
            findings.append(
                Finding(
                    "status.invalid",
                    FAIL,
                    f"{path}.status {status!r} is invalid; use one of: {', '.join(STATUSES)}.",
                    path=f"{path}.status",
                    expected=list(STATUSES),
                    actual=status,
                )
            )
        elif status == "inferred":
            findings.append(
                Finding(
                    "status.inferred",
                    WARN,
                    f"{path} is inferred, not read from the datasheet; a human should confirm it.",
                    path=f"{path}.status",
                )
            )
    return findings


_QUOTE_NUMBER = re.compile(r"\d+(?:\.\d+)?|\.\d+")
# A drawing that prints inches quotes sizes like `.012-.020` where the spec records 0.31-0.51:
# the conversion absorbs the rounding each way, so two per cent of the recorded value.
_UNIT_TOLERANCE = 0.02
_INCH_MM = 25.4


def _carries(value: float, numbers: list[float]) -> bool:
    """True when a quote number is the recorded value, or that number read in inches."""
    return any(
        abs(n - value) <= _UNIT_TOLERANCE * value or abs(n * _INCH_MM - value) <= _UNIT_TOLERANCE * value
        for n in numbers
    )


def check_quote_value_support(spec: PartSpec) -> list[Finding]:
    """An extracted dimension must be readable from its own quote (SRC-006).

    A quote may sit on the cited page and still be the wrong evidence: `SEATING PLANE`
    with a `nom` of 1.55 supports nothing.  A numberless quote is a dimension-letter row
    (`HE L Lp v w y`) whose values live in a separate row of the text layer, and an
    `inferred` dimension is a human-flagged interpretation; both are left alone.
    """
    findings: list[Finding] = []
    for name, dim in spec.package.dimensions.items():
        path = f"package.dimensions.{name}"
        if dim.status != "extracted":
            continue
        if dim.source is None or not dim.source.quote.strip():
            continue  # check_provenance owns a missing or empty quote
        numbers = [float(item) for item in _QUOTE_NUMBER.findall(dim.source.quote)]
        if not numbers:
            continue
        values = [value for value in (dim.min, dim.nom, dim.max) if value is not None]
        if any(_carries(value, numbers) for value in values):
            continue
        recorded = {
            label: value for label, value in (("min", dim.min), ("nom", dim.nom), ("max", dim.max)) if value is not None
        }
        findings.append(
            Finding(
                "dim.quote_unsupported",
                FAIL,
                f"{path} records {recorded} but quote {dim.source.quote!r} carries no number matching any of them "
                "(a callout quoted in inches counts, converted): quote the row or callout the value was read from.",
                path=path,
                actual={"recorded": recorded, "quote_numbers": numbers},
            )
        )
    return findings


_PAREN_NUMBER = re.compile(r"(?<![A-Za-z0-9])\(\s*(?P<value>\d+(?:\.\d+)?)\s*\)")


def check_reference_dimensions(spec: PartSpec) -> list[Finding]:
    """A parenthesised value never becomes a package dimension (DIM-004).

    A quote may incidentally show a reference value next to a real one — pca9306's lead_length row
    carries `(0.13) TYP` — so the test is on what was recorded: a non-`land_*` dimension whose
    recorded value its own quote prints in parentheses. A boxed `BASIC` value is the same rule with
    no textual marker; the prose covers it.
    """
    findings: list[Finding] = []
    for name, dim in spec.package.dimensions.items():
        if name.startswith("land_"):
            continue
        if dim.source is None or not dim.source.quote.strip():
            continue  # check_provenance owns a missing or empty quote
        parenthesised = [float(m.group("value")) for m in _PAREN_NUMBER.finditer(dim.source.quote)]
        if not parenthesised:
            continue
        recorded = {
            label: value for label, value in (("min", dim.min), ("nom", dim.nom), ("max", dim.max)) if value is not None
        }
        for label, value in recorded.items():
            if _carries(value, parenthesised):
                findings.append(
                    Finding(
                        "dim.reference_value",
                        FAIL,
                        f"package.dimensions.{name}.{label} {value} is printed parenthesised in quote "
                        f"{dim.source.quote!r}: a parenthesised value is a reference dimension, usable only for "
                        "a land_* value — drop the dimension when it is the only callout for it on the sheet.",
                        path=f"package.dimensions.{name}",
                        actual={"recorded": recorded, "parenthesised": parenthesised},
                    )
                )
    return findings


SPEC_CHECKS: tuple[Callable[[PartSpec], list[Finding]], ...] = (
    check_provenance,
    check_pin_count,
    check_pin_numbers_unique,
    check_electrical_types,
    check_dimension_order,
    check_quote_value_support,
    check_reference_dimensions,
    check_statuses,
)
