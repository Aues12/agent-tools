from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


OPERATOR_MAP = {
    "Add": "addition",
    "Sub": "subtraction",
    "Mult": "multiplication",
    "Div": "division",
    "Mod": "modulo",
    "Pow": "power",
    "Eq": "equals",
    "NotEq": "not_equals",
    "Lt": "less_than",
    "Gt": "greater_than",
    "LtE": "less_than_or_equal",
    "GtE": "greater_than_or_equal",
}


class SemanticASTParser:
    def __init__(self, file_path: str | Path | None = None):
        self.file_path = str(file_path) if file_path else None

    def parse_code(self, code: str) -> dict:
        tree = ast.parse(code)
        return self.normalize(tree)

    def parse_file(self, file_path: str | Path) -> dict:
        path = Path(file_path)

        code = path.read_text(encoding="utf-8")

        self.file_path = str(path)

        tree = ast.parse(code)

        return self.normalize(tree)

    def normalize(self, node: Any):

        if isinstance(node, list):
            return [self.normalize(x) for x in node]

        if not isinstance(node, ast.AST):
            return node

        method_name = f"visit_{type(node).__name__}"

        visitor = getattr(self, method_name, self.generic_visit)

        return visitor(node)

    def add_metadata(self, node: ast.AST, result: dict):

        result["line"] = getattr(node, "lineno", None)
        result["end_line"] = getattr(node, "end_lineno", None)

        if self.file_path:
            result["file"] = self.file_path

        return result

    def generic_visit(self, node: ast.AST):

        result = {
            "type": type(node).__name__.lower()
        }

        for field_name, value in ast.iter_fields(node):
            result[field_name] = self.normalize(value)

        return self.add_metadata(node, result)

    def visit_Module(self, node: ast.Module):

        result = {
            "type": "module",
            "body": self.normalize(node.body)
        }

        return self.add_metadata(node, result)

    def visit_Assign(self, node: ast.Assign):

        result = {
            "type": "assignment",
            "targets": self.normalize(node.targets),
            "value": self.normalize(node.value)
        }

        return self.add_metadata(node, result)

    def visit_Name(self, node: ast.Name):

        result = {
            "type": "variable",
            "name": node.id
        }

        return self.add_metadata(node, result)

    def visit_Constant(self, node: ast.Constant):

        result = {
            "type": "constant",
            "value": node.value
        }

        return self.add_metadata(node, result)

    def visit_BinOp(self, node: ast.BinOp):

        operator_name = type(node.op).__name__

        result = {
            "type": OPERATOR_MAP.get(operator_name, operator_name.lower()),
            "left": self.normalize(node.left),
            "right": self.normalize(node.right)
        }

        return self.add_metadata(node, result)

    def visit_FunctionDef(self, node: ast.FunctionDef):

        result = {
            "type": "function",
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "body": self.normalize(node.body)
        }

        return self.add_metadata(node, result)

    def visit_ClassDef(self, node: ast.ClassDef):

        result = {
            "type": "class",
            "name": node.name,
            "bases": [self.normalize(base) for base in node.bases],
            "body": self.normalize(node.body)
        }

        return self.add_metadata(node, result)

    def visit_Return(self, node: ast.Return):

        result = {
            "type": "return",
            "value": self.normalize(node.value)
        }

        return self.add_metadata(node, result)

    def visit_Call(self, node: ast.Call):

        result = {
            "type": "function_call",
            "function": self.normalize(node.func),
            "args": self.normalize(node.args)
        }

        return self.add_metadata(node, result)


if __name__ == "__main__":

    parser = SemanticASTParser()

    code = """
class Engine:
    def run(self, x):
        y = x + 1
        return y
"""

    result = parser.parse_code(code)

    from pprint import pprint

    pprint(result)
```

---

# Example Output

"""
{
    'type': 'module',
    'body': [
        {
            'type': 'class',
            'name': 'Engine',
            'body': [
                {
                    'type': 'function',
                    'name': 'run',
                    'args': ['self', 'x'],
                    'body': [
                        {
                            'type': 'assignment',
                            'targets': [
                                {
                                    'type': 'variable',
                                    'name': 'y'
                                }
                            ],
                            'value': {
                                'type': 'addition',
                                'left': {
                                    'type': 'variable',
                                    'name': 'x'
                                },
                                'right': {
                                    'type': 'constant',
                                    'value': 1
                                }
                            }
                        },
                        {
                            'type': 'return',
                            'value': {
                                'type': 'variable',
                                'name': 'y'
                            }
                        }
                    ]
                }
            ]
        }
    ]
}
```

---

# Why This Structure Is Useful

This semantic AST representation is:

* more human-readable
* more compact than raw AST output
* easier for LLMs to understand
* easier to serialize as JSON
* useful for code navigation tools
* useful for agent workflows

Potential future extensions:

* dependency graphs
* call graphs
* symbol indexing
* import analysis
* code chunk extraction
* AST-based refactoring
* semantic search
"""