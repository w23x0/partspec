"""Publish a complete, new artifact directory without overwriting earlier work."""

from __future__ import annotations

import json
import math
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}; keep one unambiguous value")
        result[key] = value
    return result


def _finite_float(text: str) -> float:
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f"JSON number {text!r} exceeds the supported finite range")
    return value


def _reject_constant(text: str) -> Any:
    raise ValueError(f"{text} is not a finite JSON number")


def parse_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=_unique_object, parse_float=_finite_float, parse_constant=_reject_constant)


def read_json(path: Path) -> Any:
    try:
        return parse_json(path.read_text(encoding="utf-8-sig"))
    except ValueError as exc:
        raise ValueError(f"{path}: {exc}") from exc


def relocate_paths(data: Any, source: Path, destination: Path) -> Any:
    """Rebase generated absolute paths when publishing a staged bundle."""
    if isinstance(data, str):
        prefix = str(source) + "/"
        if data == str(source):
            return str(destination)
        return str(destination) + "/" + data[len(prefix):] if data.startswith(prefix) else data
    if isinstance(data, list):
        return [relocate_paths(item, source, destination) for item in data]
    if isinstance(data, dict):
        return {key: relocate_paths(value, source, destination) for key, value in data.items()}
    return data


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


@contextmanager
def artifact_directory(destination: Path) -> Iterator[Path]:
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f"{destination} already exists; choose a new output directory to preserve earlier work")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".partspec-", dir=destination.parent) as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        yield staging
        if destination.exists():
            raise FileExistsError(f"{destination} was created while working; choose a new output directory")
        staging.rename(destination)


def workspace_path(root: Path, value: str) -> Path:
    """Resolve paths, including symlinks, within the caller's explicit workspace."""
    root = root.resolve()
    candidate = Path(value).expanduser()
    result = (candidate if candidate.is_absolute() else root / candidate).resolve()
    if not result.is_relative_to(root):
        raise ValueError(f"{value!r} is outside workspace {root}; use a path inside it")
    return result
