"""Import an exported KiCad XML netlist without invoking KiCad or guessing pins."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any
from xml.etree import ElementTree

from kicad_partspec.findings import FAIL, WARN, Finding, failed

MAX_NETLIST_BYTES = 16 * 1024 * 1024
_SCALE = {"": 1.0, "R": 1.0, "r": 1.0, "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9,
          "m": 1e-3, "u": 1e-6, "U": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15}


def passive_value(text: str, kind: str) -> float:
    """Read complete EDA value labels, preserving the difference between m and M."""
    if not isinstance(text, str) or kind not in ("resistor", "capacitor"):
        raise ValueError("pass a resistor or capacitor value label")
    label = re.sub(r"\s+", "", text).replace("µ", "u").replace("μ", "u")
    if kind == "resistor":
        label = re.sub(r"(?:ohms?|Ω)$", "", label, flags=re.IGNORECASE)
        prefixes = "RrkKMmG"
    else:
        explicit_farads = label.endswith("F")
        if explicit_farads:
            label = label[:-1]
        prefixes = "muUnpf"
        if not explicit_farads and not any(prefix in label for prefix in prefixes):
            raise ValueError("a capacitor label needs a scale or F unit; supply capacitance_f when ambiguous")
    embedded = re.fullmatch(rf"(\d+)([{prefixes}])(\d+)", label)
    if embedded:
        value = float(f"{embedded[1]}.{embedded[3]}") * _SCALE[embedded[2]]
    else:
        match = re.fullmatch(rf"((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)([{prefixes}]?)", label)
        if not match:
            raise ValueError(f"cannot interpret the complete {kind} label {text!r}; supply its numeric SI value explicitly")
        value = float(match[1]) * _SCALE[match[2]]
    if not math.isfinite(value) or value < 0 or (kind == "capacitor" and value == 0):
        raise ValueError(f"invalid {kind} value {text!r}")
    return value


def import_xml(
    xml: bytes, bindings: Any, specs: dict[str, Any], *, requirements: Any = None, unconnected: Any = None,
) -> tuple[dict[str, Any] | None, list[Finding]]:
    """bindings key each actual reference; specs already holds the explicitly bound PartSpecs."""
    findings: list[Finding] = []

    def error(code: str, message: str, path: str = "") -> None:
        findings.append(Finding(f"netlist.{code}", FAIL, message, path=path))

    if not isinstance(xml, bytes) or len(xml) > MAX_NETLIST_BYTES:
        error("input", "supply a KiCad XML netlist of at most 16 MiB")
        return None, findings
    if not isinstance(bindings, dict) or not bindings:
        error("bindings", "bindings must map every netlist reference to a PartSpec or an explicit passive kind")
        return None, findings
    try:
        # Exported KiCad XML needs no custom entities or external definitions.
        if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
            raise ValueError("DTD/entity declarations are not supported; use KiCad's XML export")
        root = ElementTree.fromstring(xml)
        if root.tag != "export" or root.find("components") is None or root.find("nets") is None:
            raise ValueError("expected a KiCad XML <export> with components and nets")
    except (ElementTree.ParseError, ValueError) as exc:
        error("xml", str(exc))
        return None, findings
    circuit: dict[str, Any] = {
        "schema": "partspec.circuit/v1", "parts": {}, "components": [], "nets": [],
        "requirements": requirements if requirements is not None else [],
        "unconnected": dict(unconnected) if isinstance(unconnected, dict) else {},
        "imported_from": {"format": "kicad-xml", "sha256": hashlib.sha256(xml).hexdigest()},
    }
    if unconnected is not None and not isinstance(unconnected, dict):
        error("unconnected", "unconnected must map ref.pin to a reason")
    refs: set[str] = set()
    for node in root.findall("./components/comp"):
        ref = node.get("ref", "")
        if not ref.strip() or "." in ref or ref in refs:
            error("reference", "each exported component needs a unique non-empty reference without dots", ref)
            continue
        refs.add(ref)
        binding = bindings.get(ref)
        if not isinstance(binding, dict):
            error("binding_missing", f"bind {ref} explicitly; components are never silently dropped", ref)
            continue
        value = (node.findtext("value") or "").strip()
        footprint = (node.findtext("footprint") or "").strip()
        dnp = node.find("dnp") is not None or any(
            (prop.get("name") or "").lower() == "dnp"
            and (prop.get("value") or "").lower() not in ("false", "no", "0")
            for prop in node.findall("property")
        )
        populated = binding.get("populated", not dnp)
        if not isinstance(populated, bool):
            error("population", "populated must be a boolean", ref)
            continue
        component: dict[str, Any] = {
            "ref": ref, "netlist_value": value, "netlist_footprint": footprint,
            "populated": populated, "netlist_populated": not dnp,
        }
        if populated != (not dnp):
            findings.append(Finding("netlist.population_override", WARN,
                                    f"{ref} population explicitly overridden from {not dnp} to {populated}; confirm the intended assembly variant",
                                    path=ref))
        if "expected_footprint" in binding:
            expected = binding["expected_footprint"]
            if not isinstance(expected, str) or not expected or footprint != expected:
                error("footprint_mismatch", f"{ref} footprint {footprint!r} differs from expected {expected!r}", ref)
        if "spec_path" in binding:
            if "kind" in binding:
                error("binding", "bind either spec_path or a passive kind, not both", ref)
                continue
            spec = specs.get(ref)
            if not isinstance(spec, dict):
                error("spec_missing", f"the bound PartSpec for {ref} could not be loaded", ref)
                continue
            circuit["parts"][ref] = spec
            component.update(kind="part", part=ref)
            if value != spec.get("mpn"):
                findings.append(Finding("netlist.value_mismatch", WARN,
                                        f"{ref} value {value!r} differs from PartSpec mpn {spec.get('mpn')!r}; review the explicit binding",
                                        path=ref))
        elif binding.get("kind") in ("resistor", "capacitor"):
            kind = binding["kind"]
            quantity = "resistance_ohm" if kind == "resistor" else "capacitance_f"
            try:
                number = binding[quantity] if quantity in binding else passive_value(value, kind)
            except ValueError as exc:
                error("value", f"{ref}: {exc}", ref)
                continue
            component.update(kind=kind, **{quantity: number})
            component["value_origin"] = "binding" if quantity in binding else "netlist_label"
        else:
            error("binding", "provide spec_path or kind resistor/capacitor; names and reference prefixes are not pin definitions", ref)
            continue
        for key in ("tolerance", "rated_voltage_v"):
            if key in binding:
                component[key] = binding[key]
        circuit["components"].append(component)
    for ref in bindings.keys() - refs:
        error("unused_binding", f"binding {ref!r} has no component in the netlist; check the selected export", str(ref))
    for node in root.findall("./nets/net"):
        name = node.get("name", "")
        pins = []
        marked_unused = []
        nodes = node.findall("node")
        if not name.strip() or not nodes:
            error("net", "each net needs its exported name and at least one node")
            continue
        for terminal in nodes:
            ref, pin = terminal.get("ref", ""), terminal.get("pin", "")
            if not ref or not pin:
                error("terminal", f"net {name!r} has a node without ref or physical pin")
                continue
            endpoint = f"{ref}.{pin}"
            if "no_connect" in (terminal.get("pintype") or "").split("+"):
                marked_unused.append(endpoint)
            pins.append(endpoint)
        if marked_unused:
            if len(pins) != 1:
                error("no_connect", f"net {name!r} connects a no-connect marker to other terminals")
            else:
                circuit["unconnected"].setdefault(pins[0], "Explicit no-connect marker in the imported KiCad XML.")
            continue
        if len(pins) == 1 and pins[0] in circuit["unconnected"]:
            continue
        if len(pins) == 1:
            findings.append(Finding("netlist.isolated_pin", WARN,
                                    f"{pins[0]} is alone on net {name!r}; check for missing wiring or document an external connection",
                                    path=pins[0]))
        circuit["nets"].append({"name": name, "pins": pins})
    if not refs:
        error("components", "the netlist contains no components")
    return (None if failed(findings) else circuit), findings
