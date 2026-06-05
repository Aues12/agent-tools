# Runtime

The runtime coordinates skills, tools, state, and memory.

Responsibilities:

* dispatch tool calls.
* execute skill steps.
* record events.
* update state through a central path.
* leave tools deterministic and inspectable.

The runtime intentionally does not implement tool-specific behavior. Tool
capabilities stay inside `file-tools/`; the runtime only discovers and invokes
them through the registry contract.
