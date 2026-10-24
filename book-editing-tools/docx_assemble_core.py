"""Apply a validated chapter plan to a new DOCX without touching the source."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile

from chapter_plan_core import validate_plan
from common import inventory, normalize, require_path


def assemble(path: str, parts: list[dict] | None = None, *,
             articles: list[int | str] | None = None, output_path: str | None = None,
             expected_preview_sha256: str | None = None, article_level: int = 1,
             dry_run: bool = True, toc_mode: str = "static_unpaged",
             contents_title: str = "Contents") -> dict:
    """Return a dry-run report or write a new file using exclusive creation.

    `toc_mode=static_unpaged` makes a contents list without misleading page numbers.
    `toc_mode=none` removes an existing automatic TOC and adds no replacement.
    """
    if not isinstance(dry_run, bool):
        raise ValueError("dry_run must be a boolean")
    if toc_mode not in {"none", "static_unpaged"}:
        raise ValueError("toc_mode must be none or static_unpaged")
    if not isinstance(contents_title, str) or not contents_title.strip():
        raise ValueError("contents_title must be non-empty text")
    plan = validate_plan(path, parts, articles=articles, article_level=article_level)
    if not plan["valid"]:
        raise ValueError(f"Invalid chapter plan: {plan['errors']}")
    if article_level not in (1, 2):
        raise ValueError("article_level must be 1 or 2")
    source = require_path(path)
    if source.suffix.lower() != ".docx":
        raise ValueError("docx_assemble requires a DOCX source")
    destination = None
    if output_path is not None:
        destination = Path(output_path).expanduser().resolve()
        if destination.suffix.lower() != ".docx":
            raise ValueError("output_path must end in .docx")
        if destination == source:
            raise ValueError("output_path must differ from source")
        if not destination.parent.is_dir():
            raise ValueError("output parent directory does not exist")
        if destination.exists():
            raise ValueError("output_path already exists; overwriting is not supported")
    try:
        from docx import Document
        from docx.enum.style import WD_STYLE_TYPE
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Pt, RGBColor
        from docx.text.paragraph import Paragraph
    except ImportError as exc:
        raise ValueError("python-docx is required; install the book-editing extra") from exc

    doc = Document(source)
    body = doc.element.body
    paragraph_tag = qn("w:p")
    section_tag = qn("w:sectPr")
    sections = [element for element in body if element.tag == section_tag]
    if len(doc.sections) != 1 or len(sections) != 1 or body[-1] is not sections[0]:
        raise ValueError("Only a single final DOCX section is supported")

    # Identify top-level article blocks; paragraph order must match the inventory.
    groups = []
    current = None
    old_part_heads = []
    for element in list(body):
        if element.tag == section_tag:
            continue
        if element.tag == paragraph_tag:
            paragraph = Paragraph(element, doc._body)
            level = _paragraph_heading_level(paragraph)
            if article_level == 2 and level == 1:
                old_part_heads.append(element)
                current = None
                continue
            if level == article_level:
                current = []
                groups.append(current)
        if current is not None:
            current.append(element)
    if len(groups) != plan["source_count"]:
        raise ValueError("DOCX article headings do not match the validated inventory")
    preface = list(body)[:list(body).index(groups[0][0])] if groups else []
    if groups:
        for element in preface:
            if element.tag == paragraph_tag and normalize(Paragraph(element, doc._body).text) in {
                    "contents", "tableofcontents", "icindekiler", "icindekilertablosu"}:
                raise ValueError("Existing contents list requires manual review before assembly")
    toc_blocks = [element for element in body if element.tag == qn("w:sdt")
                  and any("TOC " in (node.text or "") for node in element.iter(qn("w:instrText")))]
    if any(element not in preface for element in toc_blocks):
        raise ValueError("Automatic table of contents outside the preface requires manual review")
    if len(toc_blocks) > 1:
        raise ValueError("Multiple automatic tables of contents require manual review")
    source_items = inventory(str(source), article_level=article_level)["items"]
    for item, group in zip(source_items, groups):
        if Paragraph(group[0], doc._body).text != item["title"]:
            raise ValueError(f"DOCX article order changed near {item['title']}")
    if sha256(source.read_bytes()).hexdigest() != plan["source_sha256"]:
        raise ValueError("Source changed during preflight; rerun preview")
    preview_sha256 = _preview_digest(plan, destination, toc_mode, contents_title.strip())
    preflight_warnings = (["Source automatic TOC will be replaced"] if toc_blocks else [])
    if dry_run:
        return {"dry_run": True, "source": str(source), "source_sha256": plan["source_sha256"],
                "preview_sha256": preview_sha256, "output_path": str(destination) if destination else None,
                "layout": plan["layout"], "article_count": plan["planned_count"],
                "part_count": len(plan["parts"]), "toc_mode": toc_mode,
                "warnings": plan["warnings"] + preflight_warnings}
    if destination is None:
        raise ValueError("output_path is required when dry_run is false")
    if expected_preview_sha256 != preview_sha256:
        raise ValueError("expected_preview_sha256 does not match source, plan, destination, or options; rerun dry-run")

    _ensure_heading_styles(doc, WD_STYLE_TYPE, Pt, RGBColor)
    target_article_level = 2 if plan["layout"] == "parts" else 1
    for group in groups:
        Paragraph(group[0], doc._body).style = doc.styles[f"Heading {target_article_level}"]
        for element in group[1:]:
            if element.tag == paragraph_tag:
                paragraph = Paragraph(element, doc._body)
                if _paragraph_heading_level(paragraph) == article_level + 1:
                    paragraph.style = doc.styles[f"Heading {target_article_level + 1}"]
    for group in groups:
        for element in group:
            body.remove(element)
    for element in old_part_heads:
        if element.getparent() is body:
            body.remove(element)
    for element in toc_blocks:
        body.remove(element)

    if toc_mode == "static_unpaged":
        _add_contents(doc, body, plan, contents_title.strip(),
                      OxmlElement, Paragraph, WD_STYLE_TYPE, Pt, RGBColor)

    insertion = len(body) - 1
    if plan["layout"] == "parts":
        for part in plan["parts"]:
            element = OxmlElement("w:p")
            paragraph = Paragraph(element, doc._body)
            paragraph.style = doc.styles["Heading 1"]
            paragraph.add_run(part["title"])
            paragraph.paragraph_format.page_break_before = True
            paragraph.paragraph_format.keep_with_next = True
            body.insert(insertion, element)
            insertion += 1
            for article in part["articles"]:
                for element in groups[article["ordinal"] - 1]:
                    body.insert(insertion, element)
                    insertion += 1
    else:
        for article in plan["articles"]:
            for element in groups[article["ordinal"] - 1]:
                body.insert(insertion, element)
                insertion += 1

    # An empty final paragraph can become an otherwise blank last page.
    if body[-2].tag == paragraph_tag and not Paragraph(body[-2], doc._body).text.strip():
        body.remove(body[-2])

    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".docx-assemble-", suffix=".docx",
                                         dir=destination.parent, delete=False) as handle:
            temporary = Path(handle.name)
        doc.save(temporary)
        after = inventory(str(temporary), article_level=target_article_level)["items"]
        expected = [source_items[article["ordinal"] - 1] for article in plan["articles"]]
        if len(after) != len(expected) or any(
                actual["title"] != original["title"] or actual["body_sha256"] != original["body_sha256"]
                for actual, original in zip(after, expected)):
            raise ValueError("Output verification failed: an article body changed")
        os.link(temporary, destination)  # atomic, fails if the destination appeared meanwhile
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

    return {"dry_run": False, "source": str(source), "source_sha256": plan["source_sha256"],
            "preview_sha256": preview_sha256, "layout": plan["layout"],
            "output_path": str(destination), "output_sha256": sha256(destination.read_bytes()).hexdigest(),
            "article_count": len(after), "part_count": len(plan["parts"]), "toc_mode": toc_mode,
            "warnings": plan["warnings"] + (["Replaced source automatic TOC"] if toc_blocks else [])
            + ["Render the DOCX for visual and pagination review"]}


def _preview_digest(plan: dict, destination: Path | None, toc_mode: str,
                    contents_title: str) -> str:
    subject = {"source_sha256": plan["source_sha256"], "layout": plan["layout"],
               "parts": [{"title": part["title"],
                          "ordinals": [article["ordinal"] for article in part["articles"]]}
                         for part in plan["parts"]],
               "articles": [article["ordinal"] for article in plan["articles"]],
               "article_level": plan["article_level"], "output_path": str(destination) if destination else None,
               "toc_mode": toc_mode, "contents_title": contents_title}
    canonical = json.dumps(subject, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _paragraph_heading_level(paragraph) -> int | None:
    name = paragraph.style.name.lower().replace(" ", "")
    for level in (1, 2, 3):
        if name in {f"heading{level}", f"başlık{level}"}:
            return level
    return None


def _ensure_heading_styles(doc, style_type, pt, rgb):
    if "Heading 3" not in doc.styles:
        style = doc.styles.add_style("Heading 3", style_type.PARAGRAPH)
        style.base_style = doc.styles["Heading 2"]
    for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 11)):
        style = doc.styles[name]
        style.font.name = "Cambria"
        style.font.size = pt(size)
        style.font.bold = True
        style.font.color.rgb = rgb(0, 0, 0)
        style.paragraph_format.keep_with_next = True


def _add_contents(doc, body, plan, contents_title, element_class, paragraph_class, style_type, pt, rgb):
    heading = doc.styles.add_style("Book Contents Title", style_type.PARAGRAPH)
    heading.font.name = "Cambria"
    heading.font.size = pt(16)
    heading.font.bold = True
    heading.font.color.rgb = rgb(0, 0, 0)
    lines = doc.styles.add_style("Book Contents Entry", style_type.PARAGRAPH)
    lines.font.name = "Cambria"
    lines.font.size = pt(10)
    lines.font.color.rgb = rgb(0, 0, 0)
    lines.paragraph_format.space_after = pt(2)
    entries = [(contents_title, True)]
    if plan["layout"] == "parts":
        for part in plan["parts"]:
            entries.append((part["title"], True))
            entries.extend((article["title"], False) for article in part["articles"])
    else:
        entries.extend((article["title"], True) for article in plan["articles"])
    for index, (title, strong) in enumerate(entries):
        element = element_class("w:p")
        paragraph = paragraph_class(element, doc._body)
        paragraph.style = heading if index == 0 else lines
        paragraph.paragraph_format.left_indent = pt(0 if strong else 14)
        run = paragraph.add_run(title)
        run.bold = strong and index != 0
        body.insert(index, element)
