# Book editing tools

Six small, read-only tools for recurring manuscript checks. They use Python 3.11+ and the standard library; no document renderer or network service is required. Place a request on stdin and read a JSON envelope on stdout. Paths may be absolute. Source files are never changed. For a large Markdown archive, pass `limit` and `offset` to `manuscript_inventory`; `count` remains the full count and `next_offset` tells the agent where to continue.

| Tool | Input | Result |
| --- | --- | --- |
| `manuscript_inventory` | DOCX, MD, or Markdown directory | Article headings, dates, order, body hashes, warnings |
| `index_audit` | DOCX with “Yazı Serileri Dizini”; optional separate index DOCX | Unique article coverage, omissions, unresolved entries |
| `chronology_audit` | DOCX, MD, or Markdown directory | Out-of-order pairs and undated articles |
| `overlap_audit` | Two or more manuscripts or collections | Exact normalized-title overlaps |
| `edition_diff` | Old and new manuscript | Added, removed, position changed, and body changed articles |
| `ebook_preflight` | DOCX | Long blank runs and image format/layout candidates |

## Fast agent workflow

1. Run `manuscript_inventory` to confirm Heading 1 detection and dates.
2. Run one focused audit. Treat `warnings`, `unmatched_entries`, and `ambiguous_titles` as unresolved, not as silent matches.
3. Present a short report and source locations. Ask an agent to judge thematic grouping, spelling, or editorial intent; these tools do not infer those.

Example from repository root:

```bash
printf '%s' '{"operation":"manuscript_inventory","params":{"path":"/absolute/path/book.docx"}}' | python3 book-editing-tools/manuscript_inventory/tool.py
```

Use the matching `operation` and `tool.py` path for each sub-tool. The full parameter and output contract is in each `SKILL.yaml`; runnable request shapes are in each `examples/request.json`. For Python callers, import each sub-tool's `tool.py` and call `run(payload)`, or import the functions in `common.py` from this directory.

## Scope and limits

DOCX extraction reads headings styled as Word Heading 1 (including localized “Başlık 1”) and sections before a “Yazı Serileri Dizini” heading. A DOCX that uses visual formatting instead of heading styles needs manual review. Markdown directories represent one article per `.md` file and read a simple `title`/`date` front matter or first `#` heading. Dates must be standalone `DD.MM.YYYY` paragraphs or ISO-style metadata. This is extraction, not full YAML parsing.

Index matching allows only unique, conservative aliases: a numbered “İlke” prefix or a trailing bracketed subtitle may be omitted. Alias matches are listed separately. Similarity suggestions are never counted as coverage. Overlap detection compares titles, not text identity. The edition comparison uses article order and body hashes; a changed hash is a signal to inspect the text, not a semantic diff.

DOCX does not contain trustworthy final page positions. Page-number checks therefore require a rendered PDF and are outside this toolset. `ebook_preflight` finds candidates in source DOCX; the resulting EPUB must still be visually checked. Editorial decisions belong in the book's `AGENTS.md` or editorial notes rather than an automatic log.

## Tests

```bash
python3 book-editing-tools/run_tests.py
```
