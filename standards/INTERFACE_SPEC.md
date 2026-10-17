# Purpose

This document defines how executable tools communicate with callers such as
humans, agents, and external orchestration systems.

The preferred executable transport model is:

```text
stdin JSON → tool → stdout JSON
```

This allows tools to be:
- subprocess-friendly
- language-independent
- sandboxable
- easily orchestrated by agent runtimes

---

# Core Philosophy

Tools should behave like small executable capabilities.

Interfaces should be:
- simple
- deterministic
- machine-readable
- transport-aware but core-logic independent

The communication layer should remain minimal.

---

# Standard Execution Flow

```text
Caller (human, agent, or host runtime)
  ↓
subprocess / shell / executor
  ↓
stdin JSON
  ↓
tool
  ↓
stdout JSON
```

---

# Input Contract

Executable tools should accept UTF-8 encoded JSON input from stdin.

The canonical request envelope is:

```json
{
  "operation": "extract_range",
  "params": {
    "file": "./AGENTS.md",
    "start": 1,
    "end": 3
  }
}
```

Recommended request fields:
- `operation`: the executable capability to invoke
- `params`: object containing operation-specific arguments
- `meta`: optional request metadata for runtimes and agents

Input validation is the responsibility of the tool.
Tools should fail fast on malformed or incomplete input.
Single-operation tools may accept a shorthand input shape only if they document
it explicitly. New integrations should prefer the canonical request envelope.

---

# Output Contract

Executable tools should return UTF-8 encoded JSON to stdout.

Successful example:

```json
{
  "success": true,
  "result": {
    "renamed": 5
  }
}
```

Recommended success fields:
- `success`: boolean
- `result`: primary payload
- `message`: human-readable summary when useful
- `meta`: optional execution metadata
  - Recommended `meta` content includes `operation` and transport details when helpful.

---

# Error Contract

Errors should be structured and machine-readable.

Example:

```json
{
  "success": false,
  "error": {
    "type": "FileNotFound",
    "message": "Directory does not exist"
  }
}
```

Tools should avoid unstructured traceback output when possible.
Diagnostics that are not part of the machine-readable result should go to stderr.

---

# Exit Codes

Recommended exit codes:

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Recoverable error |
| 2 | Invalid input |
| 3 | Runtime failure |

---

# Optional Python Interface

Python tools may additionally expose a direct callable interface:

```python
def run(input_data: dict) -> dict:
    pass
```

Recommended CLI adapter pattern:

```python
def main():
    pass
```

The transport layer should:
- read stdin JSON
- call `run()` or an equivalent core function
- print stdout JSON

Core logic should remain independent from CLI transport.
If a tool already exposes a narrower public API, `run()` may simply adapt to that API.

---

# Non-Goals

This specification does not define:
- planning behavior
- runtime orchestration
- memory systems
- agent cognition
- registry structure

These are handled by separate specifications.

---

# Design Preference

Prefer:
- composable tools
- explicit behavior
- predictable outputs
- stateless execution

Avoid:
- interactive prompts
- hidden side effects
- tightly coupled runtime behavior
