"""Read-only manuscript primitives shared by the book editing micro-tools.

DOCX is read with the Python standard library so the agents can run these
checks in a fresh environment without installing a document renderer.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from difflib import get_close_matches
from hashlib import sha256
from pathlib import Path
import json
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


def inventory(path: str, *, recursive: bool = False,
              offset: int = 0, limit: int | None = None,
              article_level: int = 1) -> dict:
    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")
    if limit is not None and (not isinstance(limit, int) or limit < 1):
        raise ValueError("limit must be a positive integer")
    if article_level not in (1, 2):
        raise ValueError("article_level must be 1 or 2")
    source = Path(path).expanduser().resolve() if isinstance(path, str) else require_path(path)
    warnings = []
    if source.is_dir():
        files = sorted(source.rglob("*.md") if recursive else source.glob("*.md"))
        items = []
        for n, file in enumerate(files, 1):
            item, item_warnings = _markdown_item(file, n)
            items.append(item)
            warnings.extend(item_warnings)
        if not files:
            warnings.append("No Markdown files found")
    elif source.is_file() and source.suffix.lower() == ".md":
        item, warnings = _markdown_item(source, 1)
        items = [item]
    elif source.is_file() and source.suffix.lower() == ".docx":
        items, warnings = _docx_items(source, article_level=article_level)
    else:
        raise ValueError(f"Expected an existing .docx, .md, or Markdown directory: {source}")
    counts = Counter(normalize(x["title"]) for x in items)
    duplicates = [x["title"] for x in items if counts[normalize(x["title"])] > 1]
    selected = items[offset:offset + limit] if limit is not None else items[offset:]
    next_offset = offset + len(selected) if offset + len(selected) < len(items) else None
    return {"source": str(source), "count": len(items), "items": selected,
            "offset": offset, "next_offset": next_offset,
            "duplicate_titles": sorted(set(duplicates)), "article_level": article_level,
            "warnings": warnings}


def index_audit(path: str, *, index_path: str | None = None,
                index_heading: str = "Yazı Serileri Dizini") -> dict:
    main = inventory(path)
    document = read_docx(index_path or path)
    paragraphs = document["paragraphs"]
    start = next((i for i, p in enumerate(paragraphs)
                  if normalize(p["text"]) == normalize(index_heading)), None)
    if start is None:
        raise ValueError(f"Index heading not found: {index_heading}")
    entries = []
    for p in paragraphs[start + 1:]:
        if _is_heading_one(p):
            break
        if "\t" not in p["text"]:
            continue
        title, page = p["text"].split("\t", 1)
        if title.strip():
            entries.append({"title": title.strip(), "page_text": page.strip(),
                            "paragraph": p["index"]})
    by_name = defaultdict(list)
    for item in main["items"]:
        by_name[normalize(item["title"])].append(item)
    matches, unknown = [], []
    for entry in entries:
        candidates = by_name.get(normalize(entry["title"]), [])
        match_type = "exact"
        if not candidates:
            variants = _title_variants(entry["title"])
            candidates = [item for item in main["items"]
                          if variants & _title_variants(item["title"])]
            match_type = "alias"
        if len(candidates) == 1:
            matches.append({**entry, "item_id": candidates[0]["id"], "match_type": match_type})
        else:
            suggestions = get_close_matches(normalize(entry["title"]), list(by_name), n=3, cutoff=.72)
            unknown.append({**entry, "reason": "ambiguous" if candidates else "unmatched",
                            "suggestions": [by_name[k][0]["title"] for k in suggestions]})
    matched = {x["item_id"] for x in matches}
    duplicate_entries = [title for title, count in Counter(normalize(x["title"]) for x in entries).items() if count > 1]
    return {"source": main["source"], "index_source": document["path"],
            "total_items": main["count"], "entry_count": len(entries),
            "covered_items": len(matched),
            "coverage_percent": round(100 * len(matched) / main["count"], 2) if main["count"] else 0,
            "unlisted": [x for x in main["items"] if x["id"] not in matched],
            "unmatched_entries": unknown, "alias_matches": [x for x in matches if x["match_type"] == "alias"],
            "duplicate_entry_keys": duplicate_entries,
            "warnings": main["warnings"]}


def chronology_audit(path: str, *, recursive: bool = False, article_level: int = 1) -> dict:
    data = inventory(path, recursive=recursive, article_level=article_level)
    items = data["items"]
    undated = [{"title": x["title"], "ordinal": x["ordinal"]} for x in items if not x["date"]]
    inversions = []
    previous = None
    for item in items:
        if item["date"]:
            if previous and item["date"] < previous["date"]:
                inversions.append({"earlier_in_book": {"title": previous["title"], "date": previous["date"], "ordinal": previous["ordinal"]},
                                   "later_in_book": {"title": item["title"], "date": item["date"], "ordinal": item["ordinal"]}})
            previous = item
    return {"source": data["source"], "count": data["count"], "dated_count": len(items) - len(undated),
            "undated": undated, "inversions": inversions, "warnings": data["warnings"]}


def overlap_audit(paths: list[str], *, recursive: bool = False) -> dict:
    if not isinstance(paths, list) or len(paths) < 2:
        raise ValueError("paths must contain at least two manuscript paths")
    sources = [inventory(p, recursive=recursive) for p in paths]
    by_name = defaultdict(list)
    for source in sources:
        for item in source["items"]:
            by_name[normalize(item["title"])].append((source["source"], item))
    exact = []
    for group in by_name.values():
        if len({collection for collection, _ in group}) > 1:
            exact.append({"title": group[0][1]["title"], "occurrences": [item for _, item in group]})
    return {"sources": [{"path": s["source"], "count": s["count"]} for s in sources],
            "exact_title_overlaps": sorted(exact, key=lambda x: normalize(x["title"])),
            "warnings": [w for s in sources for w in s["warnings"]],
            "note": "Title matches are candidates; this does not prove identical text or editorial intent."}


def edition_diff(old_path: str, new_path: str, *, old_article_level: int = 1,
                 new_article_level: int = 1) -> dict:
    old = inventory(old_path, article_level=old_article_level)
    new = inventory(new_path, article_level=new_article_level)
    def keyed(items):
        result = defaultdict(list)
        for item in items:
            result[normalize(item["title"])].append(item)
        return result
    a, b = keyed(old["items"]), keyed(new["items"])
    shared = a.keys() & b.keys()
    ambiguous = [a[k][0]["title"] for k in shared if len(a[k]) != 1 or len(b[k]) != 1]
    comparable = [k for k in shared if len(a[k]) == len(b[k]) == 1]
    return {"old_source": old["source"], "new_source": new["source"],
            "old_count": old["count"], "new_count": new["count"],
            "added": [x for x in new["items"] if normalize(x["title"]) not in a],
            "removed": [x for x in old["items"] if normalize(x["title"]) not in b],
            "moved": [{"title": b[k][0]["title"], "old_ordinal": a[k][0]["ordinal"], "new_ordinal": b[k][0]["ordinal"]}
                      for k in comparable if a[k][0]["ordinal"] != b[k][0]["ordinal"]],
            "body_changed": [{"title": b[k][0]["title"], "old_sha256": a[k][0]["body_sha256"],
                              "new_sha256": b[k][0]["body_sha256"]}
                             for k in comparable if a[k][0]["body_sha256"] != b[k][0]["body_sha256"]],
            "ambiguous_titles": ambiguous, "warnings": old["warnings"] + new["warnings"]}


def ebook_preflight(path: str, *, blank_threshold: int = 4) -> dict:
    if not isinstance(blank_threshold, int) or blank_threshold < 2:
        raise ValueError("blank_threshold must be an integer >= 2")
    doc = read_docx(path)
    paragraphs = doc["paragraphs"]
    gaps, start = [], None
    for p in paragraphs + [{"index": len(paragraphs) + 1, "text": "END"}]:
        if not p["text"].strip():
            if start is None:
                start = p["index"]
        elif start is not None:
            count = p["index"] - start
            if count >= blank_threshold:
                gaps.append({"start_paragraph": start, "count": count})
            start = None
    unsupported = [name for name in doc["media"] if Path(name).suffix.lower() in {".emf", ".wmf", ".svg"}]
    issues = []
    if gaps:
        issues.append({"code": "long_blank_runs", "count": len(gaps), "details": gaps})
    if unsupported:
        issues.append({"code": "review_media_format", "count": len(unsupported), "details": unsupported})
    if doc["floating_images"]:
        issues.append({"code": "floating_images", "count": doc["floating_images"]})
    return {"source": doc["path"], "paragraph_count": len(paragraphs),
            "media_count": len(doc["media"]), "inline_images": doc["inline_images"],
            "floating_images": doc["floating_images"], "default_language": doc["default_language"],
            "issues": issues, "note": "Preflight flags candidates; verify the rendered EPUB separately."}

OPERATIONS = {"manuscript_inventory": inventory, "index_audit": index_audit,
              "chronology_audit": chronology_audit, "overlap_audit": overlap_audit,
              "edition_diff": edition_diff, "ebook_preflight": ebook_preflight}


def run_request(operation: str, payload: dict) -> dict:
    try:
        if not isinstance(payload, dict) or payload.get("operation") != operation or not isinstance(payload.get("params"), dict):
            raise ValueError(f"Expected {{'operation': '{operation}', 'params': {{...}}}}")
        result = OPERATIONS[operation](**payload["params"])
        return {"success": True, "message": f"{operation} completed", "result": result,
                "meta": {"operation": operation, "read_only": True}}
    except (TypeError, ValueError, OSError) as exc:
        return {"success": False, "message": str(exc), "result": None,
                "error": {"type": type(exc).__name__, "message": str(exc)},
                "meta": {"operation": operation, "read_only": True}}


def cli(operation: str) -> None:
    import sys
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError) as exc:
        payload = {}
    response = run_request(operation, payload)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    raise SystemExit(0 if response["success"] else 1)
