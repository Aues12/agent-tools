# Book editing tools

Eight small tools for recurring manuscript work. Six existing audits and the new `chapter_plan` validator are read-only; `docx_assemble` writes only to a new output path. Read-only tools use Python 3.11+ and the standard library. DOCX assembly additionally needs `python-docx` (`pip install -e '.[book-editing]'`). Place a request on stdin and read a JSON envelope on stdout. Source files are never changed. For a large Markdown archive, pass `limit` and `offset` to `manuscript_inventory`; `count` remains the full count and `next_offset` tells the agent where to continue.

| Tool | Input | Result |
| --- | --- | --- |
| `manuscript_inventory` | DOCX, MD, or Markdown directory | Article headings, dates, order, body hashes, warnings |
| `index_audit` | DOCX with “Yazı Serileri Dizini”; optional separate index DOCX | Unique article coverage, omissions, unresolved entries |
| `chronology_audit` | DOCX, MD, or Markdown directory | Out-of-order pairs and undated articles |
| `overlap_audit` | Two or more manuscripts or collections | Exact normalized-title overlaps |
| `edition_diff` | Old and new manuscript | Added, removed, position changed, and body changed articles |
| `ebook_preflight` | DOCX | Long blank runs and image format/layout candidates |
| `chapter_plan` | Manuscript and explicit ordered part/article plan | Full-coverage, uniqueness, and chronological-order validation |
| `docx_assemble` | DOCX, validated plan, new output path | Dry-run or new chaptered DOCX with article-body verification |

## Fast agent workflow

1. Run `manuscript_inventory` to confirm article headings and dates. Set `article_level: 2` when Heading 1 denotes parts and Heading 2 denotes articles.
2. Run a focused audit and draft an explicit plan. Treat `warnings`, `unmatched_entries`, and `ambiguous_titles` as unresolved, not as silent matches.
3. Run `chapter_plan` before assembly. The plan has `parts: [{"title": "Part title", "articles": [1, 2]}]`, where article references are source ordinals or unique titles. Every article must occur exactly once; exact-date inversions invalidate the plan.
4. Run `docx_assemble` first with its default `dry_run: true`. For a write, pass `dry_run: false`, `output_path` pointing to a nonexistent DOCX, and the returned `source_sha256` as `expected_source_sha256`. Inspect the result in Word or a rendered PDF before publication.

Example from repository root:

```bash
printf '%s' '{"operation":"manuscript_inventory","params":{"path":"/absolute/path/book.docx"}}' | python3 book-editing-tools/manuscript_inventory/tool.py
```

Use the matching `operation` and `tool.py` path for each sub-tool. The full parameter and output contract is in each `SKILL.yaml`; runnable request shapes are in each `examples/request.json`. For Python callers, import each sub-tool's `tool.py` and call `run(payload)`, or import the functions in `common.py` from this directory.

## Scope and limits

DOCX extraction reads headings styled as Word Heading 1 or, with `article_level: 2`, Heading 2 (including localized “Başlık”). A DOCX that uses visual formatting instead of heading styles needs manual review. Markdown directories represent one article per `.md` file and read a simple `title`/`date` front matter or first `#` heading. Dates must be standalone `DD.MM.YYYY` paragraphs (optionally marked `[yaklaşık tarih]` or `[y.t.]`) or ISO-style metadata. Approximate dates are reported and inversions involving them are warnings. This is extraction, not full YAML parsing.

Index matching allows only unique, conservative aliases: a numbered “İlke” prefix or a trailing bracketed subtitle may be omitted. Alias matches are listed separately. Similarity suggestions are never counted as coverage. Overlap detection compares titles, not text identity. The edition comparison uses article order and body hashes; a changed hash is a signal to inspect the text, not a semantic diff.

DOCX does not contain trustworthy final page positions. Page-number checks therefore require a rendered PDF and are outside this toolset. `ebook_preflight` finds candidates in source DOCX; the resulting EPUB must still be visually checked. Editorial decisions belong in the book's `AGENTS.md` or editorial notes rather than an automatic log.

`docx_assemble` rearranges article XML blocks without editing article prose, demotes article headings under new Heading 1 part headings, and verifies article titles/body hashes. Its optional contents list is static and deliberately has no page numbers; set `contents_title` for the document language. A single Word automatic TOC before the first article is removed and replaced; manually typed contents lists and unsupported multiple-section layouts are rejected at write time. Other complex front matter, headers, footers, bookmarks, and cross-references require manual inspection. It does not replace visual proofing or editorial review.

## Tests

```bash
python3 book-editing-tools/run_tests.py
```
