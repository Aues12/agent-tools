# copy_paste Tool Instructions

This tool provides deterministic text transfer primitives for files.

Local rules:

* Use 1-based line numbers for public range and insertion APIs.
* Treat `extract_range` start and end as inclusive.
* Validate all line numbers before writing.
* Keep file writes limited to the target path passed by the caller.
* Do not update registry, memory, or state from this tool.
* Prefer explicit text matching over implicit semantic selection.

Future semantic selection should live in a locator tool such as `find_block`.
