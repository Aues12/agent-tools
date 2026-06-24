from __future__ import annotations

import sys
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from schema import DFGEdge, DFGNode  # noqa: E402


class SemanticDfgSchemaTests(unittest.TestCase):
    def test_node_to_dict_omits_empty_values(self) -> None:
        node = DFGNode(
            id="function:sample.main:parameter:path",
            name="path",
            kind="parameter",
            scope="sample.main",
            flow_level=0,
            depth=0,
        )

        self.assertEqual(
            node.to_dict(),
            {
                "id": "function:sample.main:parameter:path",
                "name": "path",
                "kind": "parameter",
                "scope": "sample.main",
                "flow_level": 0,
                "depth": 0,
            },
        )

    def test_edge_to_dict_preserves_operation_and_line(self) -> None:
        edge = DFGEdge(
            source="function:sample.main:parameter:path",
            target="function:sample.main:binding:text",
            kind="depends_on",
            operation="read_file",
            lineno=2,
        )

        self.assertEqual(edge.to_dict()["operation"], "read_file")
        self.assertEqual(edge.to_dict()["lineno"], 2)


if __name__ == "__main__":
    unittest.main()
