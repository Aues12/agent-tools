"""Read DOCX and Markdown sources into article-ready records."""
from __future__ import annotations

from datetime import date
from hashlib import sha256
from pathlib import Path
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
DATE_LINE = re.compile(r"^\s*(\d{1,2})[./-](\d{1,2})[./-](\d{4})(?:\s*\[(yaklaşık tarih|y\.t\.)\])?\s*$", re.I)
ISO_DATE = re.compile(r"^\s*(\d{4})-(\d{2})-(\d{2})(?:[T ].*)?$", re.I)


def normalize(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value).casefold().replace("ı", "i")
    return "".join(c for c in folded if c.isalnum())


def _title_variants(value: str) -> set[str]:
    """Conservative aliases for numbered series entries and subtitle omissions."""
    base = re.sub(r"^\s*\d+\.\s*İlke\s*[—–:-]\s*", "", value, flags=re.I)
    without_subtitle = re.sub(r"\s*\[[^]]+\]\s*$", "", base)
    return {normalize(base), normalize(without_subtitle)}


def require_path(value: str, *, directory: bool = False) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A non-empty path is required")
    path = Path(value).expanduser().resolve()
    if directory and not path.is_dir():
        raise ValueError(f"Not a directory: {path}")
    if not directory and not path.is_file():
        raise ValueError(f"Not a file: {path}")
    return path


def _paragraph_text(paragraph: ET.Element) -> str:
    parts = []
    for branch in paragraph:
        if branch.tag == W + "pPr":
            continue
        for child in branch.iter():
            if child.tag == W + "t":
                parts.append(child.text or "")
            elif child.tag == W + "tab":
                parts.append("\t")
            elif child.tag == W + "br":
                parts.append("\n")
    return "".join(parts)


def _style_names(archive: zipfile.ZipFile) -> dict[str, str]:
    if "word/styles.xml" not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read("word/styles.xml"))
    result = {}
    for style in root.iter(W + "style"):
        name = style.find(W + "name")
        if name is not None:
            result[style.get(W + "styleId", "")] = name.get(W + "val", "")
    return result


def read_docx(path: str | Path) -> dict:
    path = require_path(str(path))
    if path.suffix.lower() != ".docx":
        raise ValueError(f"Expected .docx: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
            names = _style_names(archive)
            paragraphs = []
            body = root.find(W + "body")
            if body is None:
                raise ValueError("DOCX has no document body")
            # Table paragraphs are included in document order, which also keeps
            # captions and index entries visible to audits.
            for element in body.iter(W + "p"):
                pstyle = element.find("./" + W + "pPr/" + W + "pStyle")
                style_id = pstyle.get(W + "val", "") if pstyle is not None else ""
                outline = element.find("./" + W + "pPr/" + W + "outlineLvl")
                level = outline.get(W + "val") if outline is not None else None
                paragraphs.append({"index": len(paragraphs) + 1,
                                   "text": _paragraph_text(element),
                                   "style_id": style_id,
                                   "style_name": names.get(style_id, style_id),
                                   "outline_level": level})
            media = sorted(n for n in archive.namelist() if n.startswith("word/media/") and not n.endswith("/"))
            anchors = sum(1 for _ in root.iter(WP + "anchor"))
            inline = sum(1 for _ in root.iter(WP + "inline"))
            language = None
            if "word/styles.xml" in archive.namelist():
                styles = ET.fromstring(archive.read("word/styles.xml"))
                default = styles.find("./" + W + "docDefaults/" + W + "rPrDefault/" + W + "rPr/" + W + "lang")
                if default is not None:
                    language = default.get(W + "val")
            return {"path": str(path), "paragraphs": paragraphs, "media": media,
                    "floating_images": anchors, "inline_images": inline,
                    "default_language": language}
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        raise ValueError(f"Invalid DOCX: {path}: {exc}") from exc


def _is_heading_one(paragraph: dict) -> bool:
    return _heading_level(paragraph) == 1


def _heading_level(paragraph: dict) -> int | None:
    style = normalize(paragraph["style_name"])
    for level in (1, 2, 3):
        if style in {f"heading{level}", f"baslik{level}"}:
            return level
    outline = paragraph["outline_level"]
    if outline in {"0", "1", "2"}:
        return int(outline) + 1
    return None


def _date_details(text: str) -> tuple[str | None, str | None]:
    match = ISO_DATE.match(text)
    if match:
        y, m, d = map(int, match.groups())
        status = "exact"
    else:
        match = DATE_LINE.match(text)
        if not match:
            return None, None
        d, m, y = map(int, match.groups()[:3])
        status = "approximate" if match.group(4) else "exact"
    try:
        return date(y, m, d).isoformat(), status
    except ValueError:
        return None, None


def _date_from_text(text: str) -> str | None:
    return _date_details(text)[0]


def _item(title: str, source: str, ordinal: int, paragraph: int | None,
          body: list[str], when: str | None, *, date_status: str | None = None,
          part: str | None = None, heading_level: int | None = None) -> dict:
    content = "\n".join(s.strip() for s in body if s.strip())
    return {"id": f"{source}#{ordinal}", "title": title.strip(), "date": when,
            "date_status": date_status, "part": part, "heading_level": heading_level,
            "source": source, "ordinal": ordinal, "paragraph": paragraph,
            "body_sha256": sha256(content.encode("utf-8")).hexdigest(),
            "body_characters": len(content)}


def _docx_items(path: Path, *, article_level: int = 1) -> tuple[list[dict], list[str]]:
    doc = read_docx(path)
    paragraphs = doc["paragraphs"]
    boundary = next((i for i, p in enumerate(paragraphs)
                     if normalize(p["text"]) == normalize("Yazı Serileri Dizini")), len(paragraphs))
    heads = [i for i, p in enumerate(paragraphs[:boundary]) if _heading_level(p) == article_level]
    warnings = []
    if not heads:
        warnings.append(f"No Heading {article_level} paragraphs found; check the DOCX heading styles")
    items = []
    for n, start in enumerate(heads):
        next_head = heads[n + 1] if n + 1 < len(heads) else boundary
        stop = next((i for i in range(start + 1, next_head)
                     if (_heading_level(paragraphs[i]) or 99) < article_level), next_head)
        section = paragraphs[start + 1:stop]
        dates = [_date_details(p["text"]) for p in section if p["text"].strip()]
        dates = [x for x in dates if x[0]]
        if len({x[0] for x in dates}) > 1:
            warnings.append(f"Multiple standalone dates under heading {n + 1}: {paragraphs[start]['text']}")
        body = [p["text"] for p in section]
        part = next((p["text"].strip() for p in reversed(paragraphs[:start])
                     if _heading_level(p) == article_level - 1), None) if article_level > 1 else None
        items.append(_item(paragraphs[start]["text"], str(path), n + 1,
                           paragraphs[start]["index"], body, dates[-1][0] if dates else None,
                           date_status=dates[-1][1] if dates else None,
                           part=part, heading_level=article_level))
    return items, warnings


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip("'\"")
    return result


def _markdown_item(path: Path, ordinal: int) -> tuple[dict, list[str]]:
    text = path.read_text(encoding="utf-8-sig")
    meta = _frontmatter(text)
    heading = next((m.group(1).strip() for line in text.splitlines()
                    if (m := re.match(r"^#\s+(.+)$", line))), None)
    title = meta.get("title") or heading or path.stem
    date_value = _date_from_text(meta.get("date", ""))
    if not date_value:
        date_value = next((x for line in text.splitlines()[-12:]
                           if (x := _date_from_text(line))), None)
    warnings = [] if meta.get("title") or heading else [f"Title from filename: {path}"]
    return _item(title, str(path), ordinal, 1 if heading else None,
                 text.splitlines(), date_value, date_status="exact" if date_value else None), warnings
