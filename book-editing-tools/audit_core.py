"""Read-only audits built on the manuscript inventory."""
from __future__ import annotations

from collections import Counter, defaultdict
from difflib import get_close_matches
from pathlib import Path

from inventory_core import inventory
from manuscript_sources import _is_heading_one, _title_variants, normalize, read_docx

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
