"""Deterministic checks of a reference circuit's connectivity and explicit requirements.

This accepts a netlist, not a drawing guessed from an image. It does not run a
simulator, route a PCB, or claim that all electrical requirements were specified.
"""

from __future__ import annotations

import math
from typing import Any

from kicad_partspec.findings import FAIL, WARN, Finding, failed
from kicad_partspec.spec import load_spec
from kicad_partspec.verify import verify_spec


def _number(value: Any, *, zero: bool = False) -> bool:
    try:
        return (not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
                and (value >= 0 if zero else value > 0))
    except OverflowError:
        return False


def check_circuit(data: Any) -> dict[str, Any]:
    findings: list[Finding] = []
    measurements: list[dict[str, Any]] = []
    connectivity_state = "not_run"
    requested_requirements = 0

    def error(code: str, message: str, path: str = "", **values: Any) -> None:
        findings.append(Finding(f"circuit.{code}", FAIL, message, path=path, **values))

    def report() -> dict[str, Any]:
        return {
            "schema": "partspec.circuit-report/v1", "passed": not failed(findings),
            "findings": [finding.to_dict() for finding in findings], "requirements": measurements,
            "coverage": {"connectivity": connectivity_state, "requirements_requested": requested_requirements,
                         "requirements_evaluated": len(measurements),
                         "datasheet_quotes": "not_checked", "simulation": "not_run",
                         "pcb_layout": "not_checked", "physical_validation": "not_run"},
        }

    if not isinstance(data, dict) or data.get("schema") != "partspec.circuit/v1":
        error("schema", "use a JSON object with schema partspec.circuit/v1")
        return report()
    parts = data.get("parts", {})
    if not isinstance(parts, dict):
        error("schema", "parts must map catalog keys to inline PartSpec documents", "parts")
        return report()
    pin_maps: dict[str, dict[str, str]] = {}
    for key, raw in parts.items():
        issues = verify_spec(raw)
        for finding in issues:
            findings.append(Finding(finding.id, finding.status, finding.message,
                                    path=f"parts.{key}.{finding.path.lstrip('.')}",
                                    expected=finding.expected, actual=finding.actual))
        spec, _ = load_spec(raw)
        if spec is not None and not failed(issues):
            pin_maps[key] = {pin.number: pin.electrical_type for pin in spec.pins}
    components = data.get("components")
    nets = data.get("nets")
    if not isinstance(components, list) or not components or not isinstance(nets, list) or not nets:
        error("schema", "components and nets must be non-empty lists")
        return report()
    catalog: dict[str, dict[str, Any]] = {}
    terminals: dict[str, str] = {}
    for index, component in enumerate(components):
        path = f"components[{index}]"
        if not isinstance(component, dict):
            error("schema", "each component must be an object", path)
            continue
        ref = component.get("ref")
        if not isinstance(ref, str) or not ref.strip() or "." in ref or ref in catalog:
            error("reference", "component ref must be unique, non-empty and contain no dot", path)
            continue
        kind = component.get("kind")
        if not isinstance(component.get("populated", True), bool):
            error("population", "populated must be a boolean; false means not fitted in this assembly", path)
            continue
        if kind == "part":
            key = component.get("part")
            if not isinstance(key, str) or key not in pin_maps:
                error("part_missing", "component.part must name a valid PartSpec in parts", path)
                continue
            pins = pin_maps[key]
        elif kind in ("capacitor", "resistor"):
            quantity = "capacitance_f" if kind == "capacitor" else "resistance_ohm"
            if not _number(component.get(quantity), zero=kind == "resistor"):
                error("value", f"{quantity} must be a finite SI number; do not use strings like 10uF", path)
                continue
            if "tolerance" in component and (not _number(component["tolerance"], zero=True) or component["tolerance"] >= 1):
                error("tolerance", "tolerance must be a fractional number from 0 inclusive to 1 exclusive", path)
                continue
            if "rated_voltage_v" in component and not _number(component["rated_voltage_v"]):
                error("voltage", "rated_voltage_v must be a finite positive number", path)
                continue
            pins = {"1": "passive", "2": "passive"}
        else:
            error("kind", "component kind must be part, capacitor or resistor", path)
            continue
        catalog[ref] = component
        terminals.update({f"{ref}.{pin}": kind for pin, kind in pins.items()})
    connections: dict[str, str] = {}
    net_names: set[str] = set()
    for index, net in enumerate(nets):
        path = f"nets[{index}]"
        if not isinstance(net, dict):
            error("schema", "each net must be an object with name and pins", path)
            continue
        name, pins = net.get("name"), net.get("pins")
        if not isinstance(name, str) or not name.strip() or name in net_names:
            error("net_name", "net names must be unique non-empty strings", path)
            continue
        net_names.add(name)
        if not isinstance(pins, list) or not pins:
            error("net_pins", "net.pins must be a non-empty list of ref.pin strings", path)
            continue
        for pin in pins:
            if not isinstance(pin, str) or pin not in terminals:
                error("pin_missing", f"unknown terminal {pin!r}; use physical pin numbers from its PartSpec", path)
            elif pin in connections:
                error("pin_reused", f"{pin} already belongs to net {connections[pin]}; merge the nets explicitly", path)
            elif terminals[pin] == "no_connect":
                error("no_connect", f"{pin} is a no-connect pin and must not be wired", path)
            else:
                connections[pin] = name
        drivers = [pin for pin in pins if isinstance(pin, str) and terminals.get(pin) in ("output", "power_out")
                   and catalog[pin.split(".", 1)[0]].get("populated", True)]
        if len(set(drivers)) > 1:
            error("driver_conflict", f"net {name} joins multiple driven outputs: {drivers}; check the topology", path)
    unused = data.get("unconnected", {})
    if not isinstance(unused, dict):
        error("schema", "unconnected must map ref.pin to a reason", "unconnected")
        unused = {}
    for pin, reason in unused.items():
        if pin not in terminals or pin in connections or not isinstance(reason, str) or not reason.strip():
            error("unconnected", f"{pin}: declare only an existing, unwired pin and explain why it is unused", "unconnected")
    for pin, kind in terminals.items():
        if pin not in connections and pin not in unused and kind != "no_connect":
            error("unwired", f"{pin} has no net; connect it or document it in unconnected", pin)
    connectivity_state = "failed" if failed(findings) else "passed"
    requirements = data.get("requirements", [])
    if not isinstance(requirements, list):
        error("schema", "requirements must be a list", "requirements")
        return report()
    if not requirements:
        findings.append(Finding("circuit.no_requirements", WARN,
                                "only connectivity was checked; provide explicit requirements for circuit intent"))
    requested_requirements = len(requirements)
    ids: set[str] = set()
    for index, requirement in enumerate(requirements):
        path = f"requirements[{index}]"
        if not isinstance(requirement, dict):
            error("schema", "each requirement must be an object", path)
            continue
        identifier, kind = requirement.get("id"), requirement.get("kind")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in ids:
            error("requirement_id", "requirement id must be a unique non-empty string", path)
            continue
        ids.add(identifier)
        actual: Any = None
        expected: Any = None
        passed = False
        if kind in ("same_net", "separate_nets"):
            pins = requirement.get("pins")
            if (not isinstance(pins, list) or len(pins) < 2
                    or any(not isinstance(pin, str) or pin not in connections for pin in pins)
                    or len(set(pins)) != len(pins)):
                error("requirement", "pins must name at least two different connected terminals", path)
                continue
            actual = {pin: connections[pin] for pin in pins}
            expected = kind
            passed = len(set(actual.values())) == (1 if kind == "same_net" else len(pins))
        elif kind == "capacitance_between":
            pair, minimum, basis = requirement.get("nets"), requirement.get("min_f"), requirement.get("basis", "minimum")
            if (not isinstance(pair, list) or len(pair) != 2
                    or any(not isinstance(net, str) or net not in net_names for net in pair)
                    or pair[0] == pair[1] or not _number(minimum) or basis not in ("minimum", "nominal")):
                error("requirement", "provide two different existing nets, positive min_f and basis minimum or nominal", path)
                continue
            candidates = [(ref, component) for ref, component in catalog.items()
                          if component["kind"] == "capacitor"
                          and component.get("populated", True)
                          and {connections.get(ref + ".1"), connections.get(ref + ".2")} == set(pair)]
            unknown = [ref for ref, component in candidates if basis == "minimum" and "tolerance" not in component]
            if unknown:
                error("tolerance_required", f"minimum capacitance needs tolerance for {unknown}; supply it or explicitly request nominal", path)
                continue
            total = sum(component["capacitance_f"] * (1 - component["tolerance"] if basis == "minimum" else 1)
                        for _, component in candidates)
            if not _number(total, zero=True):
                error("value", "combined capacitance exceeds the finite numeric range", path)
                continue
            actual = {"farads": total, "basis": basis, "components": [ref for ref, _ in candidates]}
            expected = {"min_f": minimum}
            passed = total >= minimum or math.isclose(total, minimum, rel_tol=1e-12, abs_tol=0)
        elif kind == "voltage_rating":
            ref, minimum = requirement.get("ref"), requirement.get("min_v")
            if not isinstance(ref, str) or ref not in catalog or not _number(minimum):
                error("requirement", "provide an existing component ref and positive min_v", path)
                continue
            if not catalog[ref].get("populated", True):
                error("unpopulated_required", f"{ref} is not populated; it cannot satisfy a required voltage rating", path)
                continue
            actual = catalog[ref].get("rated_voltage_v")
            expected = {"min_v": minimum}
            passed = _number(actual) and actual >= minimum
        else:
            error("requirement_kind", f"unsupported requirement kind {kind!r}; use same_net, separate_nets, capacitance_between or voltage_rating", path)
            continue
        measurements.append({"id": identifier, "kind": kind, "passed": passed, "actual": actual, "expected": expected})
        if not passed:
            error("requirement_failed", f"requirement {identifier!r} failed; correct the circuit or the documented requirement", path,
                  expected=expected, actual=actual)
    return report()
