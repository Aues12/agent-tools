"""Exact, guarded search and replacement for UTF-8 Markdown and DOCX body text."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import zipfile
from xml.parsers import expat
from xml.sax.saxutils import escape

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def search_token(source_sha256, query):
    return digest(
        json.dumps(
            [source_sha256, query], ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
    )


def _docx_segments(xml):
    """Return safe adjacent text nodes; retain byte offsets for minimal XML edits."""
    if xml.startswith((b"\xff\xfe", b"\xfe\xff")) or b"<!DOCTYPE" in xml.upper():
        raise ValueError("Only UTF-8 DOCX XML without DTD is supported")
    parser = expat.ParserCreate(namespace_separator="}")

    def xml_declaration(version, encoding, standalone):
        if encoding is not None and encoding.lower().replace("-", "") != "utf8":
            raise ValueError("Only UTF-8 DOCX XML is supported")

    parser.XmlDeclHandler = xml_declaration
    stack, segments, current, para = [], [], None, 0
    token = None
    field_depth = 0
    unsafe = set()

    def barrier():
        nonlocal current
        current = None

    def start(name, attrs):
        nonlocal token, current, para, field_depth
        parent = stack[-1] if stack else ""
        if name == W + "p":
            para += 1
            if field_depth:
                unsafe.add(para)
            barrier()
        elif (
            name == W + "t"
            and parent == W + "r"
            and len(stack) >= 2
            and stack[-2] == W + "p"
            and W + "txbxContent" not in stack
        ):
            # Scan the start tag respecting quoted attributes.
            i = parser.CurrentByteIndex
            quote = None
            while i < len(xml):
                c = xml[i]
                if quote:
                    if c == quote:
                        quote = None
                elif c in (34, 39):
                    quote = c
                elif c == 62:
                    break
                i += 1
            if i >= len(xml) or xml[i - 1 : i + 1] == b"/>":
                barrier()
            else:
                token = {
                    "start": i + 1,
                    "tag_start": parser.CurrentByteIndex,
                    "text": "",
                    "paragraph": para,
                }
        elif parent == W + "p" and name not in (W + "pPr", W + "r"):
            unsafe.add(para)
            barrier()
        elif parent == W + "r" and name not in (W + "rPr", W + "t"):
            unsafe.add(para)
            barrier()
            if name == W + "fldChar":
                kind = attrs.get(W + "fldCharType")
                if kind == "begin":
                    field_depth += 1
                elif kind == "end":
                    field_depth = max(0, field_depth - 1)
        stack.append(name)

    def chars(data):
        if token is not None:
            token["text"] += data

    def end(name):
        nonlocal token, current
        if name == W + "t" and token is not None:
            token["end"] = parser.CurrentByteIndex
            if current is None:
                current = {"paragraph": para, "nodes": []}
                segments.append(current)
            current["nodes"].append(token)
            token = None
        if name == W + "p":
            barrier()
        stack.pop()

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.CharacterDataHandler = chars
    parser.Parse(xml, True)
    return [s for s in segments if s["paragraph"] not in unsafe], len(unsafe)


def _load(path):
    p = Path(path)
    if p.suffix.lower() not in (".md", ".docx"):
        raise ValueError("Only .md and .docx files are supported")
    data = p.read_bytes()
    if p.suffix.lower() == ".md":
        return (
            p,
            data,
            [{"paragraph": None, "nodes": [{"text": data.decode("utf-8")}]}],
            0,
        )
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            if z.namelist().count("word/document.xml") != 1:
                raise ValueError("DOCX must contain exactly one document.xml")
            xml = z.read("word/document.xml")
        segments, unsafe = _docx_segments(xml)
        return p, data, segments, unsafe
    except (zipfile.BadZipFile, KeyError, expat.ExpatError) as exc:
        raise ValueError("Invalid or unsupported DOCX: " + str(exc)) from exc


def _matches(segments, query):
    matches = []
    for si, seg in enumerate(segments):
        text = "".join(n["text"] for n in seg["nodes"])
        pos = 0
        while True:
            pos = text.find(query, pos)
            if pos < 0:
                break
            match = {
                "id": len(matches) + 1,
                "segment": si,
                "start": pos,
                "end": pos + len(query),
                "context": text[max(0, pos - 60) : pos + len(query) + 60],
            }
            if seg["paragraph"] is not None:
                match["paragraph"] = seg["paragraph"]
            else:
                match["line"] = text.count("\n", 0, pos) + 1
            matches.append(match)
            pos += len(query)
    return matches


def _validate_query(query):
    if not isinstance(query, str) or not query:
        raise ValueError("query must be a non-empty string")
    if any(ord(c) < 32 and c not in "\t\n\r" for c in query):
        raise ValueError("query contains invalid control characters")


def search(path, query):
    _validate_query(query)
    p, data, segments, unsafe = _load(path)
    found = _matches(segments, query)
    return {
        "path": str(p),
        "query": query,
        "source_sha256": digest(data),
        "search_token": search_token(digest(data), query),
        "count": len(found),
        "matches": found,
        "warnings": (
            [
                f"{unsafe} DOCX paragraphs contain unsupported structures and were skipped entirely."
            ]
            if unsafe
            else []
        )
        + (
            [
                "DOCX search covers the main document body and tables only, not headers, footers, footnotes or text boxes."
            ]
            if p.suffix.lower() == ".docx"
            else []
        ),
    }


def replace(
    path,
    query,
    replacement,
    source_sha256,
    search_token,
    expected_count,
    match_ids,
    output_path,
):
    _validate_query(query)
    if not isinstance(replacement, str):
        raise ValueError("replacement must be a string")
    if any(ord(c) < 32 and c not in "\t\n\r" for c in replacement):
        raise ValueError("replacement contains invalid control characters")
    if (
        not isinstance(expected_count, int)
        or isinstance(expected_count, bool)
        or expected_count < 1
    ):
        raise ValueError("expected_count must be a positive integer")
    if (
        not isinstance(match_ids, list)
        or not match_ids
        or any(not isinstance(x, int) or isinstance(x, bool) for x in match_ids)
        or len(set(match_ids)) != len(match_ids)
    ):
        raise ValueError("match_ids must be a non-empty list of unique integers")
    p, data, segments, unsafe = _load(path)
    if digest(data) != source_sha256:
        raise ValueError("Source changed since search; search again")
    if search_token != globals()["search_token"](source_sha256, query):
        raise ValueError("Search token does not match source and query")
    found = _matches(segments, query)
    if len(found) != expected_count:
        raise ValueError(f"Expected {expected_count} matches; found {len(found)}")
    if any(x < 1 or x > len(found) for x in match_ids):
        raise ValueError("match_ids contains an unknown match")
    out = Path(output_path)
    if out.suffix.lower() != p.suffix.lower():
        raise ValueError("output extension must match source")
    if out.resolve() == p.resolve():
        raise ValueError("output must differ from source")
    if p.suffix.lower() == ".docx" and any(c in replacement for c in "\n\r\t"):
        raise ValueError("DOCX replacement cannot contain tabs or line breaks")
    selected = [found[i - 1] for i in sorted(match_ids)]
    if p.suffix.lower() == ".md":
        text = data.decode("utf-8")
        for m in reversed(selected):
            text = text[: m["start"]] + replacement + text[m["end"] :]
        output = text.encode("utf-8")
    else:
        # Modify only the text-node byte ranges; all other package parts stay unchanged.
        with zipfile.ZipFile(io.BytesIO(data)) as src:
            xml = src.read("word/document.xml")
            patches = []
            for si in sorted({m["segment"] for m in selected}):
                nodes = segments[si]["nodes"]
                values = [n["text"] for n in nodes]
                offsets = []
                x = 0
                for value in values:
                    offsets.append(x)
                    x += len(value)
                for m in reversed([v for v in selected if v["segment"] == si]):
                    start, end = m["start"], m["end"]
                    first = next(
                        i
                        for i in range(len(values))
                        if offsets[i] <= start < offsets[i] + len(nodes[i]["text"])
                    )
                    last = next(
                        i
                        for i in range(len(values))
                        if offsets[i] < end <= offsets[i] + len(nodes[i]["text"])
                    )
                    a, b = start - offsets[first], end - offsets[last]
                    if first == last:
                        values[first] = (
                            values[first][:a] + replacement + values[first][b:]
                        )
                    else:
                        values[first] = values[first][:a] + replacement
                        for i in range(first + 1, last):
                            values[i] = ""
                        values[last] = values[last][b:]
                for n, value in zip(nodes, values):
                    if value != n["text"]:
                        # Preserve significant leading/trailing spaces in Word text nodes.
                        tag = xml[n["tag_start"] : n["start"]]
                        if (
                            value
                            and (value[0].isspace() or value[-1].isspace())
                            and b"xml:space" not in tag
                        ):
                            patches.append(
                                (
                                    n["start"] - 1,
                                    n["start"] - 1,
                                    b' xml:space="preserve"',
                                )
                            )
                        elif (
                            value
                            and (value[0].isspace() or value[-1].isspace())
                            and b"xml:space" in tag
                            and b"preserve" not in tag
                        ):
                            raise ValueError(
                                "DOCX text node has unsupported xml:space setting"
                            )
                        patches.append(
                            (n["start"], n["end"], escape(value).encode("utf-8"))
                        )
            for a, b, v in sorted(patches, reverse=True):
                xml = xml[:a] + v + xml[b:]
            try:
                _docx_segments(xml)
            except expat.ExpatError as exc:
                raise ValueError("Replacement produces invalid DOCX XML") from exc
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as dst:
                dst.comment = src.comment
                for info in src.infolist():
                    dst.writestr(
                        info,
                        xml if info.filename == "word/document.xml" else src.read(info),
                    )
            output = buf.getvalue()
    try:
        with out.open("xb") as f:
            f.write(output)
    except FileExistsError:
        raise ValueError("output already exists") from None
    return {
        "output_path": str(out),
        "source_sha256": source_sha256,
        "output_sha256": digest(output),
        "replacement_count": len(selected),
        "match_ids": sorted(match_ids),
        "unsupported_paragraphs": unsafe,
    }
