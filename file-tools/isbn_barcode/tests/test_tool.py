from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import (  # noqa: E402
    calculate_check_digit,
    encode_ean13,
    generate_svg,
    run,
    validate_isbn13,
    verify_svg,
    write_svg,
)


KNOWN_ISBN = "9786253798338"
KNOWN_PATTERN = (
    "101011101100010010000101001001101110010111101010101000100111010010010001"
    "00001010000101001000101"
)


class IsbnBarcodeToolTests(unittest.TestCase):
    def test_check_digit_known_vector(self) -> None:
        self.assertEqual(calculate_check_digit(KNOWN_ISBN[:12]), "8")

    def test_ean_encoding_matches_known_95_module_vector(self) -> None:
        self.assertEqual(encode_ean13(KNOWN_ISBN), KNOWN_PATTERN)
        self.assertEqual(len(KNOWN_PATTERN), 95)

    def test_generate_svg_has_nominal_layout_and_text(self) -> None:
        result = generate_svg(KNOWN_ISBN, "ISBN 978-625-379-833-8")
        root = ElementTree.fromstring(result["svg"])

        self.assertEqual(result["width_mm"], 37.29)
        self.assertEqual(result["module_count"], 95)
        self.assertEqual(root.get("width"), "37.29mm")
        self.assertIn("ISBN 978-625-379-833-8", result["svg"])

    def test_invalid_check_digit_is_rejected_not_corrected(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected 8, received 7"):
            validate_isbn13("9786253798337")

    def test_display_text_must_match_encoded_isbn(self) -> None:
        with self.assertRaisesRegex(ValueError, "must match"):
            generate_svg(KNOWN_ISBN, "ISBN 978-0-306-40615-7")

    def test_write_and_verify_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "barcode.svg"
            result = write_svg(
                KNOWN_ISBN,
                path,
                display_text="ISBN 978-625-379-833-8",
            )

            self.assertEqual(result["path"], str(path))
            self.assertTrue(result["verification"]["valid"])
            self.assertTrue(verify_svg(path, KNOWN_ISBN)["valid"])

    def test_write_refuses_overwrite_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "barcode.svg"
            path.write_text("existing", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                write_svg(KNOWN_ISBN, path)

            self.assertEqual(path.read_text(encoding="utf-8"), "existing")

    def test_verify_detects_changed_bar_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "barcode.svg"
            generated = generate_svg(KNOWN_ISBN)
            changed = generated["svg"].replace(
                'data-module="0" x="3.63"',
                'data-module="0" x="3.64"',
            )
            path.write_text(changed, encoding="utf-8")

            report = verify_svg(path, KNOWN_ISBN)

            self.assertFalse(report["valid"])
            self.assertIn(
                "a bar x-position does not match its module index",
                report["errors"],
            )

    def test_run_returns_structured_error_for_unknown_parameter(self) -> None:
        response = run(
            {
                "operation": "generate_svg",
                "params": {"isbn": KNOWN_ISBN, "unexpected": True},
            }
        )

        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["type"], "ValueError")

    def test_entrypoint_reads_stdin_json(self) -> None:
        payload = {
            "operation": "generate_svg",
            "params": {"isbn": KNOWN_ISBN},
        }
        completed = subprocess.run(
            [sys.executable, str(TOOL_DIR / "isbn_barcode.py")],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8"))
        response = json.loads(completed.stdout.decode("utf-8"))
        self.assertTrue(response["success"])
        self.assertEqual(response["result"]["isbn"], KNOWN_ISBN)


if __name__ == "__main__":
    unittest.main()
