"""Apply attributed review records to an exact PartSpec and review scope."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from kicad_partspec.findings import FAIL, Finding


def content_hash(data: Any) -> str:
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def apply_decisions(
    data: Any, targets: dict[str, dict[str, Any]], records: Any = None,
) -> tuple[dict[str, Any], list[Finding]]:
    """Records acknowledge review; they never rewrite PartSpec values or statuses."""
    findings: list[Finding] = []
    entries = {target: {"target": target, "verdict": "pending", "reviewer_kind": None,
                        "reviewer": "", "reviewed_at": "", "note": ""} for target in targets}

    def error(code: str, message: str, path: str = "") -> None:
        findings.append(Finding(f"review.{code}", FAIL, message, path=path))

    try:
        identity = {"spec_sha256": content_hash(data), "scope_sha256": content_hash(targets)}
    except (TypeError, ValueError) as exc:
        error("bad_input", f"review needs finite, JSON-serializable data: {exc}")
        identity = {"spec_sha256": None, "scope_sha256": None}

    if records is not None and not findings:
        if not isinstance(records, dict) or records.get("schema") != "partspec.review/v1":
            error("bad_decisions", "use the review-input.json template produced by review")
        elif any(records.get(key) != value for key, value in identity.items()):
            error("stale_decisions", "the PartSpec or review scope changed; review the new template before carrying decisions forward")
        elif not isinstance(records.get("decisions"), list):
            error("bad_decisions", "decisions must be a list of attributed review entries")
        else:
            accepted_entries: dict[str, dict[str, Any]] = {}
            for index, entry in enumerate(records["decisions"]):
                path = f"decisions[{index}]"
                if not isinstance(entry, dict):
                    error("bad_decisions", "each decision must be an object", path)
                    continue
                target, verdict = entry.get("target"), entry.get("verdict")
                if not isinstance(target, str) or target not in targets or target in accepted_entries:
                    error("bad_decisions", "target must name a unique item in the current review template", path)
                    continue
                if verdict not in ("pending", "accepted", "rejected", "needs_info"):
                    error("bad_decisions", "verdict must be pending, accepted, rejected or needs_info", path)
                    continue
                if verdict != "pending" and (
                    entry.get("reviewer_kind") not in ("human", "model")
                    or any(not isinstance(entry.get(key), str) or not entry[key].strip() for key in ("reviewer", "note"))
                ):
                    error("bad_decisions", "a decision needs reviewer_kind (human/model), reviewer and a non-empty note", path)
                    continue
                if verdict != "pending":
                    try:
                        timestamp = entry.get("reviewed_at")
                        if not isinstance(timestamp, str) or datetime.fromisoformat(timestamp.replace("Z", "+00:00")).utcoffset() is None:
                            raise ValueError("missing timezone")
                    except ValueError:
                        error("bad_decisions", "reviewed_at must be an ISO 8601 timestamp with a timezone", path)
                        continue
                accepted_entries[target] = (
                    {key: entry.get(key) for key in entries[target]} if verdict != "pending" else entries[target]
                )
            # A malformed or contradictory file must not clear any review work.
            if not findings:
                entries.update(accepted_entries)

    for target, entry in entries.items():
        if entry["verdict"] == "rejected":
            error("rejected", f'{entry["reviewer"]} rejected this item: {entry["note"]}', target)
    counts = {verdict: sum(entry["verdict"] == verdict for entry in entries.values())
              for verdict in ("pending", "accepted", "rejected", "needs_info")}
    complete = bool(targets) and counts["accepted"] == len(targets)
    kinds = {entry["reviewer_kind"] for entry in entries.values() if entry["verdict"] == "accepted"}
    state = "requires_review"
    if complete:
        state = "recorded_human_review" if kinds == {"human"} else "recorded_model_review" if kinds == {"model"} else "recorded_mixed_review"
    elif counts["rejected"]:
        state = "rejected"
    return {
        **identity, "state": state, "total": len(targets), **counts,
        "items": [{**entry, "subject": targets[target]} for target, entry in entries.items()],
        "input": {"schema": "partspec.review/v1", **identity, "decisions": list(entries.values())},
    }, findings
