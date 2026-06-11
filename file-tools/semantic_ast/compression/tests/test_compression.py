from __future__ import annotations

import sys
import unittest
from pathlib import Path


COMPRESSION_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMPRESSION_DIR))

from compression import compress_ast  # noqa: E402


class CompressionTests(unittest.TestCase):
    def test_compress_function_extracts_args_calls_and_lines(self) -> None:
        tree = {
            "type": "function",
            "name": "main",
            "args": {
                "positional_or_keyword": [
                    {"type": "argument", "name": "value"},
                ],
            },
            "body": [
                {
                    "type": "return",
                    "value": {
                        "type": "call",
                        "func": {"type": "name", "id": "helper"},
                        "args": [{"type": "name", "id": "value"}],
                    },
                }
            ],
            "returns": {"type": "name", "id": "int"},
            "line": 10,
            "end_line": 12,
        }

        compressed = compress_ast(tree)

        self.assertEqual(compressed["type"], "function")
        self.assertEqual(compressed["name"], "main")
        self.assertEqual(compressed["args"], ["value"])
        self.assertEqual(compressed["calls"], ["helper"])
        self.assertEqual(compressed["returns"], "int")
        self.assertEqual(compressed["line"], 10)
        self.assertEqual(compressed["end_line"], 12)

    def test_compress_class_extracts_methods_and_bases(self) -> None:
        tree = {
            "type": "class",
            "name": "Runner",
            "bases": [{"type": "name", "id": "BaseRunner"}],
            "body": [
                {"type": "function", "name": "run"},
            ],
            "line": 1,
            "end_line": 4,
        }

        compressed = compress_ast(tree)

        self.assertEqual(compressed["type"], "class")
        self.assertEqual(compressed["name"], "Runner")
        self.assertEqual(compressed["bases"], ["BaseRunner"])
        self.assertEqual(compressed["methods"], ["run"])

    def test_compress_generic_preserves_selected_fields(self) -> None:
        tree = {
            "type": "custom",
            "name": "thing",
            "body": [{"type": "name", "id": "value"}],
            "ignored": "noise",
        }

        compressed = compress_ast(tree)

        self.assertEqual(compressed, {"type": "custom", "name": "thing", "body": ["value"]})


if __name__ == "__main__":
    unittest.main()
