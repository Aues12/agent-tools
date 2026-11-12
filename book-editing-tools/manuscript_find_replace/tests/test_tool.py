import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "find_replace_tool", Path(__file__).resolve().parents[1] / "tool.py"
)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


class Tests(unittest.TestCase):
    def test_non_utf8_docx_is_rejected_before_output(self):
        src = self.root / "encoded.docx"
        xml = (
            '<?xml version="1.0" encoding="ISO-8859-1"?>'
            f'<w:document xmlns:w="{W}"><w:body>'
            "<w:p><w:r><w:t>cafe</w:t></w:r></w:p>"
            "</w:body></w:document>"
        )
        with zipfile.ZipFile(src, "w") as package:
            package.writestr("word/document.xml", xml.encode("latin1"))
        result = self.call("search", path=str(src), query="cafe")
        self.assertFalse(result["success"])
        self.assertIn("UTF-8", result["message"])
        out = self.root / "out.docx"
        result = self.call(
            "replace",
            path=str(src),
            query="cafe",
            replacement="été",
            source_sha256="unused",
            search_token="unused",
            expected_count=1,
            match_ids=[1],
            output_path=str(out),
        )
        self.assertFalse(result["success"])
        self.assertFalse(out.exists())

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def call(self, op, **kw):
        return tool.run({"operation": op, "params": kw})

    def params(self, src, query, replacement, out):
        result = self.call("search", path=str(src), query=query)["result"]
        return dict(
            path=str(src),
            query=query,
            replacement=replacement,
            output_path=str(out),
            source_sha256=result["source_sha256"],
            search_token=result["search_token"],
            expected_count=result["count"],
            match_ids=[1],
        )

    def test_markdown_selected_and_source_preserved(self):
        src = self.root / "x.md"
        src.write_bytes("varlıkı\r\nvarlıkı".encode())
        out = self.root / "out.md"
        args = self.params(src, "varlıkı", "varlığı", out)
        self.assertEqual(args["expected_count"], 2)
        self.assertTrue(self.call("replace", **args)["success"])
        self.assertEqual(out.read_bytes(), "varlığı\r\nvarlıkı".encode())
        self.assertEqual(src.read_bytes(), "varlıkı\r\nvarlıkı".encode())
        self.assertFalse(self.call("replace", **args)["success"])

    def test_guard_mismatches_and_bad_inputs(self):
        src = self.root / "x.md"
        src.write_text("abc abc")
        out = self.root / "out.md"
        a = self.params(src, "abc", "def", out)
        for change in (
            {"expected_count": 1},
            {"match_ids": [3]},
            {"match_ids": [1, 1]},
            {"query": "bc"},
            {"source_sha256": "bad"},
        ):
            self.assertFalse(self.call("replace", **(a | change))["success"])
        src.write_text("changed")
        self.assertFalse(self.call("replace", **a)["success"])
        self.assertFalse(out.exists())
        self.assertFalse(self.call("search", path=str(src), query="")["success"])

    def docx(self, body):
        src = self.root / "x.docx"
        xml = f'<w:document xmlns:w="{W}"><w:body>{body}</w:body></w:document>'.encode()
        with zipfile.ZipFile(src, "w") as z:
            z.writestr("word/document.xml", xml)
            z.writestr("custom.bin", b"unchanged")
        return src

    def test_docx_across_runs_preserves_other_xml_and_package(self):
        src = self.docx(
            "<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>var</w:t></w:r><w:r><w:t>lıkı</w:t></w:r></w:p>"
        )
        out = self.root / "out.docx"
        args = self.params(src, "varlıkı", "varlığı", out)
        self.assertTrue(self.call("replace", **args)["success"])
        with zipfile.ZipFile(out) as z:
            xml = z.read("word/document.xml")
            self.assertIn(b"<w:rPr><w:b/></w:rPr>", xml)
            self.assertIn("varlığı".encode(), xml)
            self.assertEqual(z.read("custom.bin"), b"unchanged")
        self.assertEqual(
            self.call("search", path=str(out), query="varlığı")["result"]["count"], 1
        )

    def test_docx_skips_hyperlinks_and_break_boundaries(self):
        src = self.docx(
            "<w:p><w:r><w:t>foo</w:t><w:tab/><w:t>bar</w:t></w:r><w:hyperlink><w:r><w:t>hidden</w:t></w:r></w:hyperlink></w:p>"
        )
        for query in ("foobar", "hidden"):
            r = self.call("search", path=str(src), query=query)["result"]
            self.assertEqual(r["count"], 0)
            self.assertTrue(r["warnings"])

    def test_docx_xml_escaping_and_unsafe_spaces(self):
        src = self.docx("<w:p><w:r><w:t>abc</w:t></w:r></w:p>")
        out = self.root / "out.docx"
        a = self.params(src, "abc", "a & b", out)
        self.assertTrue(self.call("replace", **a)["success"])
        self.assertEqual(
            self.call("search", path=str(out), query="a & b")["result"]["count"], 1
        )
        a = self.params(src, "abc", " x", self.root / "spaces.docx")
        self.assertTrue(self.call("replace", **a)["success"])
        with zipfile.ZipFile(self.root / "spaces.docx") as z:
            self.assertIn(b'xml:space="preserve"', z.read("word/document.xml"))

    def test_multiple_matches_one_docx_run(self):
        src = self.docx("<w:p><w:r><w:t>abc abc</w:t></w:r></w:p>")
        out = self.root / "multi.docx"
        a = self.params(src, "abc", "z", out)
        a["match_ids"] = [1, 2]
        self.assertTrue(self.call("replace", **a)["success"])
        self.assertEqual(
            self.call("search", path=str(out), query="z z")["result"]["count"], 1
        )

    def test_field_spanning_paragraphs_skipped(self):
        src = self.docx(
            '<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r></w:p><w:p><w:r><w:t>fieldvalue</w:t></w:r></w:p><w:p><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
        )
        result = self.call("search", path=str(src), query="fieldvalue")["result"]
        self.assertEqual(result["count"], 0)
        self.assertTrue(result["warnings"])
