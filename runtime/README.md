# Runtime

The runtime will become the orchestration kernel for skills, tools, state, and
memory.

Initial responsibilities:

* dispatch tool calls.
* execute skill steps.
* record events.
* update state through a central path.
* leave tools deterministic and inspectable.

Permission systems are intentionally deferred until the runtime shape is more
stable.

Current modules:

* `planner.py` normalizes explicit tool-call tasks into ordered steps.
* `executor.py` dispatches registry-backed tools through stdin/stdout JSON.
* `engine.py` coordinates planning and step execution.

The runtime intentionally does not implement tool-specific behavior. Tool
capabilities stay inside `file-tools/`; the runtime only discovers and invokes
them through the registry contract.
