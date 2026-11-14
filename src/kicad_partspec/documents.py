"""Index every PDF page and render bounded batches for visual extraction.

Poppler text remains the source of quotes. Images and page-selection heuristics
help a reader find evidence; neither is a claim that a value was verified.
"""

from __future__ import annotations

import html
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import quote as quote_url

from kicad_partspec.artifacts import artifact_directory, write_json
from kicad_partspec.verify.quotes import page_texts, sha256_of

_TOPICS = {
    "pinout": r"pin\s*(?:configuration|assignment|description|function|out)|terminal\s+functions",
    "package": r"package\s*(?:outline|drawing|dimensions|information)|mechanical\s+(?:data|dimensions)",
    "land_pattern": r"land\s+pattern|recommended\s+(?:pcb|footprint|pad)|example\s+board\s+layout|solder\s+mask",
    "ordering": r"ordering\s+(?:information|guide)|orderable|package\s+option\s+addendum",
}


def index_pages(texts: list[str], terms: list[str] | None = None) -> list[dict[str, Any]]:
    """Pure page inventory. Sparse and broken-text pages remain visible."""
    terms = [term.strip() for term in terms or [] if term.strip()]
    pages = []
    for number, text in enumerate(texts, 1):
        visible = sum(character.isalnum() for character in text)
        broken = sum(ord(c) < 32 and c not in "\n\r\t" or c == "\ufffd" for c in text)
        quality = "broken" if broken else "sparse" if visible < 40 else "searchable"
        topics = [name for name, pattern in _TOPICS.items() if re.search(pattern, text, re.IGNORECASE)]
        matches = [term for term in terms if re.search(re.escape(term), text, re.IGNORECASE)]
        pages.append({
            "page": number, "text_quality": quality, "text_characters": len(text),
            "control_or_replacement_characters": broken, "topics": topics, "term_matches": matches,
            "text_file": f"text/page-{number:04d}.txt", "preview": None,
        })
    return pages


def preview_candidates(pages: list[dict[str, Any]], limit: int) -> list[int]:
    """Reserve space for each evidence category, tail pages and text failures."""
    if limit == 0:
        return []
    groups = [
        [p["page"] for p in pages if topic in p["topics"]]
        for topic in ("pinout", "package", "land_pattern", "ordering")
    ]
    groups += [
        [p["page"] for p in pages if p["text_quality"] != "searchable"],
        [p["page"] for p in pages if p["term_matches"]],
        [p["page"] for p in pages[-12:]],
        [1] if pages else [],
    ]
    chosen: list[int] = []
    for offset in range(max((len(group) for group in groups), default=0)):
        for group in groups:
            if offset < len(group) and group[offset] not in chosen:
                chosen.append(group[offset])
                if len(chosen) >= limit:
                    return sorted(chosen)
    return sorted(chosen)


def parse_pages(expression: str, *, maximum: int | None = None) -> list[int]:
    if not isinstance(expression, str):
        raise ValueError("pages must be a string such as 1,7-9,12")
    pages: set[int] = set()
    for token in expression.split(","):
        match = re.fullmatch(r"\s*([1-9]\d*)(?:\s*-\s*([1-9]\d*))?\s*", token)
        if not match:
            raise ValueError("pages must be positive PDF page numbers, for example 1,7-9,12")
        start, end = int(match[1]), int(match[2] or match[1])
        if start > end or end - start >= 32:
            raise ValueError("use ascending page ranges and at most 32 pages per read")
        pages.update(range(start, end + 1))
        if len(pages) > 32:
            raise ValueError("read at most 32 pages at once; split a longer document into batches")
    if maximum is not None and any(page > maximum for page in pages):
        raise ValueError(f"the PDF has {maximum} pages; select pages within 1..{maximum}")
    return sorted(pages)


def _images_available() -> None:
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("pdftoppm was not found; install poppler-utils to render pages")
    try:
        from PIL import Image  # noqa: F401
    except ImportError as exc:
        raise RuntimeError('install "kicad-partspec[pdf]" for page images and contact sheets') from exc


def _render(pdf: Path, page: int, target: Path, dpi: int, crop: list[float] | None = None) -> None:
    from PIL import Image

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            ["pdftoppm", "-f", str(page), "-l", str(page), "-singlefile", "-r", str(dpi),
             "-png", str(pdf), str(target.with_suffix(""))],
            stdin=subprocess.DEVNULL, capture_output=True, timeout=120, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"rendering PDF page {page} timed out; try fewer pages or a lower dpi") from exc
    if result.returncode or not target.is_file():
        raise RuntimeError(f"cannot render PDF page {page}: {result.stderr.decode(errors='replace').strip()}")
    if crop is not None:
        with Image.open(target) as original:
            width, height = original.size
            box = (math.floor(crop[0] * width), math.floor(crop[1] * height),
                   math.ceil(crop[2] * width), math.ceil(crop[3] * height))
            cropped = original.crop(box)
        cropped.save(target)


def _contact_sheets(directory: Path, selected: list[int]) -> list[str]:
    from PIL import Image, ImageDraw, ImageOps

    sheets = []
    for start in range(0, len(selected), 12):
        batch = selected[start:start + 12]
        sheet = Image.new("RGB", (960, math.ceil(len(batch) / 4) * 350), "#e9edf2")
        draw = ImageDraw.Draw(sheet)
        for index, number in enumerate(batch):
            x, y = index % 4 * 240, index // 4 * 350
            with Image.open(directory / f"images/page-{number:04d}.png") as original:
                thumb = ImageOps.contain(original.convert("RGB"), (224, 314))
            sheet.paste(thumb, (x + (240 - thumb.width) // 2, y + 25))
            draw.text((x + 8, y + 6), f"PDF page {number}", fill="#142238")
        filename = f"contact-{start // 12 + 1:02d}.png"
        sheet.save(directory / filename)
        sheets.append(filename)
    return sheets


def _gallery(directory: Path, manifest: dict[str, Any]) -> None:
    cards = []
    for page in manifest["pages"]:
        number = page["page"]
        image = page["preview"]
        picture = (
            f'<a href="{quote_url(image, safe="/")}"><img loading="lazy" src="{quote_url(image, safe="/")}" '
            f'alt="PDF page {number}"></a>' if image else "<p>Preview not rendered.</p>"
        )
        labels = ", ".join(page["topics"]) or "No keyword match"
        cards.append(
            f'<article><h2>Page {number}</h2>{picture}<p>{html.escape(labels)}</p>'
            f'<p>Text: {page["text_quality"]}</p><a href="{quote_url(page["text_file"], safe="/")}">Full page text</a></article>'
        )
    title = html.escape(Path(manifest["pdf"]).name)
    document = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        f'<title>{title} — page inventory</title><style>body{{font:16px system-ui;margin:2rem;background:#f5f7fb;'
        'color:#17243b}}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1rem}'
        'article{background:white;padding:1rem;border:1px solid #d5deeb;border-radius:8px}img{width:100%;'
        'max-height:360px;object-fit:contain}h2{font-size:1.1rem}</style>'
        f'<h1>{title}</h1><p>All {len(manifest["pages"])} PDF pages are indexed. '
        'Keyword matches are navigation hints. Unrendered and broken-text pages still need inspection.</p>'
        f'<main>{"".join(cards)}</main></html>'
    )
    (directory / "index.html").write_text(document, encoding="utf-8")


def prepare(pdf: Path, out: Path, *, terms: list[str] | None = None, preview_limit: int = 24) -> dict[str, Any]:
    if type(preview_limit) is not int or not 0 <= preview_limit <= 32:
        raise ValueError("preview_limit must be an integer from 0 to 32; use 0 for a text-only inventory")
    if terms is not None and (not isinstance(terms, list) or any(not isinstance(term, str) for term in terms)):
        raise ValueError("terms must be a list of part numbers, package names or drawing codes")
    pdf = pdf.resolve()
    digest = sha256_of(pdf)
    texts = page_texts(pdf)
    if not texts:
        raise ValueError("the PDF has no readable page inventory")
    pages = index_pages(texts, terms)
    selected = preview_candidates(pages, preview_limit)
    if selected:
        _images_available()
    manifest: dict[str, Any] = {
        "schema": "partspec.evidence/v1", "pdf": str(pdf), "sha256": digest,
        "page_count": len(pages), "terms": terms or [], "pages": pages,
        "selection": "heuristic, not evidence of absence on other pages",
    }
    with artifact_directory(out) as staging:
        (staging / "text").mkdir()
        for page, text in zip(pages, texts):
            (staging / page["text_file"]).write_text(text, encoding="utf-8")
            if page["page"] in selected:
                page["preview"] = f'images/page-{page["page"]:04d}.png'
                _render(pdf, page["page"], staging / page["preview"], 90)
        manifest["contact_sheets"] = _contact_sheets(staging, selected) if selected else []
        if sha256_of(pdf) != digest:
            raise ValueError("the PDF changed during preparation; retry with a stable copy")
        write_json(staging / "manifest.json", manifest)
        _gallery(staging, manifest)
    return {
        "passed": True, "sha256": digest, "page_count": len(pages),
        "manifest": str(out / "manifest.json"), "gallery": str(out / "index.html"),
        "contact_sheets": [str(out / name) for name in manifest["contact_sheets"]],
        "previewed_pages": selected,
        "pages_needing_visual_read": [p["page"] for p in pages if p["text_quality"] != "searchable"],
        "unpreviewed_pages": [p["page"] for p in pages if p["preview"] is None],
        "next_step": "Inspect contact sheets, then read selected pages at higher resolution; inspect broken-text pages even without keyword matches.",
    }


def read_pages(
    pdf: Path, pages: str, out: Path, *, dpi: int = 180, crop: list[float] | None = None,
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    if type(dpi) is not int or not 72 <= dpi <= 600:
        raise ValueError("dpi must be an integer from 72 to 600")
    if crop is not None and (
        not isinstance(crop, list) or len(crop) != 4
        or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in crop)
        or not (0 <= crop[0] < crop[2] <= 1 and 0 <= crop[1] < crop[3] <= 1)
    ):
        raise ValueError("crop must be [left, top, right, bottom] in normalized page coordinates, within 0..1")
    _images_available()
    pdf = pdf.resolve()
    digest = sha256_of(pdf)
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("PDF SHA-256 differs from expected_sha256; use the PDF indexed by prepare")
    texts = page_texts(pdf)
    selected = parse_pages(pages, maximum=len(texts))
    result: dict[str, Any] = {"passed": True, "sha256": digest, "pages": []}
    with artifact_directory(out) as staging:
        for number in selected:
            image = f"images/page-{number:04d}.png"
            text_file = f"page-{number:04d}.txt"
            _render(pdf, number, staging / image, dpi, crop)
            (staging / text_file).write_text(texts[number - 1], encoding="utf-8")
            result["pages"].append({
                "page": number, "image": str(out / image), "text_file": str(out / text_file),
                "text": texts[number - 1][:8000], "text_truncated": len(texts[number - 1]) > 8000,
                "text_scope": "full page, including when the image is cropped", "image_region": crop or [0, 0, 1, 1],
            })
        result["contact_sheets"] = [str(out / name) for name in _contact_sheets(staging, selected)]
        if sha256_of(pdf) != digest:
            raise ValueError("the PDF changed while reading; retry with a stable copy")
        write_json(staging / "pages.json", result)
    return result
