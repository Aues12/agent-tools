# Runtime Layer

The `runtime/` directory contains the execution core of the agent system.

Its responsibility is orchestration, not business logic.

The runtime layer coordinates:
- planning
- execution
- task flow

but should avoid implementing tool-specific behavior directly.

---

# Core Philosophy

Keep the runtime layer:
- minimal
- modular
- stateless when possible

Tools should contain capabilities.
The runtime should coordinate capabilities.

---

# Architectural Principles

## 1. Separation of Concerns

- runtime = orchestration
- registry = discovery
- tools = actions
- memory = persistence

Do not mix these responsibilities.

---

## 2. Thin Runtime

Avoid building a monolithic runtime core.

Prefer:
- composable tools
- simple orchestration
- explicit execution flow

---

## 3. Tool Standardization

All tools should expose a consistent interface.

Recommended minimal interface:

```python
def run(input_data: dict) -> dict:
    pass
```

This allows:

* planner compatibility
* execution chaining
* predictable runtime behavior

---

## 4. Avoid Tool Logic Inside Runtime

Do not hardcode business logic into:

* engine.py
* planner.py
* executor.py

Runtime should coordinate tools,
not replace them.

---

Build the smallest system that works well.
