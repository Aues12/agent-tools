"""Build a stable inventory from manuscript sources."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from manuscript_sources import _docx_items, _markdown_item, normalize, require_path

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
