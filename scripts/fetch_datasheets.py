"""Fetch the datasheet PDFs the gold cases cite, and verify them by SHA-256.

The PDFs are deliberately not in the repository. Each gold carries the URL and
revision it was built from plus the SHA-256 of the file actually used, so a fetch
is only useful when the hash matches: the tools match datasheets by hash
(``find_datasheet``), and a vendor re-revision is a different document even when
the URL is the same.

Usage:
    .venv/bin/python scripts/fetch_datasheets.py [DIR] [--wayback] [--force]

DIR defaults to ~/datasheets (outside the repository). ``--wayback`` retries a
mismatched or failed download through a Wayback Machine snapshot of the vendor
URL, which is how the ST and Silicon Labs sheets were obtained in round 2 (both
vendors refuse scripted downloads). Exit code is 0 only when every cited PDF is
present and hash-verified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "evals" / "cases"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def cited() -> list[tuple[str, str, str]]:
    """(case, url, sha256) for every gold that cites a datasheet."""
    rows = []
    for path in sorted(CASES.glob("*/spec.gold.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        sheet = data.get("datasheet") or {}
        if sheet.get("url") and sheet.get("sha256"):
            rows.append((path.parent.name, sheet["url"], sheet["sha256"]))
    return rows


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(url: str, target: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["curl", "-sSL", "--retry", "2", "--max-time", "180", "-A", UA, "-o", str(target), url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False, f"curl exit {result.returncode}"
    if not target.is_file() or target.stat().st_size == 0:
        return False, "empty file"
    return True, ""


def wayback(url: str) -> str:
    # id_ serves the original bytes of the latest snapshot, unmodified.
    return f"https://web.archive.org/web/2id_/{url}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", default="~/datasheets", type=Path)
    parser.add_argument("--wayback", action="store_true", help="retry a failure through a Wayback snapshot")
    parser.add_argument("--force", action="store_true", help="re-download even when the file is already verified")
    args = parser.parse_args()

    target_dir = args.directory.expanduser()
    target_dir.mkdir(parents=True, exist_ok=True)

    ok, bad = [], []
    for case, url, expected in cited():
        target = target_dir / f"{case}.pdf"
        if target.is_file() and not args.force and sha256_of(target) == expected:
            ok.append(case)
            print(f"  ok       {case} (already present, hash verified)")
            continue

        got, why = fetch(url, target)
        if got and sha256_of(target) == expected:
            ok.append(case)
            print(f"  ok       {case} ({target.stat().st_size // 1024} KiB, hash verified)")
            continue

        detail = why or f"SHA-256 mismatch (got {sha256_of(target)[:12]}, want {expected[:12]})"
        if args.wayback:
            time.sleep(1)
            got, why = fetch(wayback(url), target)
            if got and sha256_of(target) == expected:
                ok.append(case)
                print(f"  ok       {case} (via Wayback, hash verified)")
                continue
            detail = why or f"SHA-256 mismatch via Wayback too (got {sha256_of(target)[:12]})"

        bad.append((case, detail))
        print(f"  FAILED   {case}: {detail}")
        if target.is_file():
            target.unlink()
        time.sleep(0.5)

    print(f"\nverified: {len(ok)}/{len(ok) + len(bad)} into {target_dir}")
    for case, detail in bad:
        print(f"  {case}: {detail}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
