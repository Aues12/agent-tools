# Runtime integration notes

This directory contains design guidance, not an executable runtime. The
repository's working capabilities are independent tools with documented
interfaces. Agents can invoke them directly; an external orchestration system
can integrate them through the same contracts.

An optional future adapter could discover tools through the registry and
coordinate calls or workflows. It should leave tool-specific behavior in each
tool and should not be required to use a tool on its own. See
[`USE_TOOL.md`](../USE_TOOL.md) for the current invocation contract and
[`FUTURE_IMPROVEMENTS.md`](../FUTURE_IMPROVEMENTS.md) for deferred ideas.
