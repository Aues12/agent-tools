# Runtime integration notes

This directory has no execution core. Treat runtime work as optional
integration with the repository's independent tools, not as a prerequisite for
using or developing them.

If adding an adapter here:

* Use the documented tool interfaces and registry metadata.
* Keep tool behavior and validation inside each tool.
* Keep agent or provider-specific integration outside the tool contracts.
* Document which behavior is implemented and which remains a proposal.

See [`../USE_TOOL.md`](../USE_TOOL.md) for the invocation contract.
