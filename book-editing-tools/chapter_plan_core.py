"""Validate an explicit chapter plan against a manuscript inventory."""
from __future__ import annotations

from hashlib import sha256

from book_model import Article, BookPlan
from common import inventory, normalize, require_path


def validate_plan(path: str, parts: list[dict] | None = None, *,
                  articles: list[int | str] | None = None, article_level: int = 1,
                  strict_chronology: bool = True) -> dict:
    layout = BookPlan.from_request(parts=parts, articles=articles)
    if not isinstance(strict_chronology, bool):
        raise ValueError("strict_chronology must be a boolean")
    source = require_path(path)
    data = inventory(str(source), article_level=article_level)
    items = [Article.from_inventory(item) for item in data["items"]]
    by_title = {}
    for item in items:
        by_title.setdefault(normalize(item.title), []).append(item)

    errors, warnings, resolved, used = [], list(data["warnings"]), [], set()
    seen_part_titles = set()
    ordered = []
    for part in layout.groups():
        title = part.title
        key = normalize(title)
        if layout.parts is not None and key in seen_part_titles:
            errors.append({"code": "duplicate_part_title", "part": title})
        seen_part_titles.add(key)
        part_items = []
        for reference in part.references:
            if isinstance(reference, int) and not isinstance(reference, bool):
                candidates = [items[reference - 1]] if 1 <= reference <= len(items) else []
            elif isinstance(reference, str) and reference.strip():
                candidates = by_title.get(normalize(reference), [])
            else:
                raise ValueError("article references must be source ordinals or non-empty titles")
            if not candidates:
                errors.append({"code": "unknown_article", "part": title, "reference": reference})
                continue
            if len(candidates) > 1:
                errors.append({"code": "ambiguous_title", "part": title, "reference": reference,
                               "ordinals": [item.ordinal for item in candidates]})
                continue
            item = candidates[0]
            if item.ordinal in used:
                errors.append({"code": "duplicate_article", "part": title,
                               "title": item.title, "ordinal": item.ordinal})
                continue
            used.add(item.ordinal)
            part_items.append(item.as_dict())
            ordered.append(item)
        if layout.parts is not None:
            resolved.append({"title": title, "articles": part_items})

    omitted = [item for item in items if item.ordinal not in used]
    if omitted:
        errors.append({"code": "omitted_articles", "ordinals": [item.ordinal for item in omitted],
                       "titles": [item.title for item in omitted]})

    previous = None
    for item in ordered:
        if not item.date:
            warnings.append(f"Undated article: {item.title}")
            continue
        if previous and item.date < previous.date:
            detail = {"code": "date_inversion", "earlier_in_plan": previous.title,
                      "later_in_plan": item.title, "earlier_date": previous.date,
                      "later_date": item.date}
            if strict_chronology and item.date_status == previous.date_status == "exact":
                errors.append(detail)
            else:
                warnings.append(detail)
        previous = item

    return {"source": str(source), "source_sha256": sha256(source.read_bytes()).hexdigest(),
            "source_count": len(items), "planned_count": len(ordered), "article_level": article_level,
            "layout": layout.layout, "valid": not errors, "parts": resolved,
            "articles": [item.as_dict() for item in ordered],
            "errors": errors, "warnings": warnings}
