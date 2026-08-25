# isbn_barcode Tool Instructions

This tool generates and verifies publication-layout ISBN-13 / EAN-13 SVG files.

Local rules:

* Keep EAN-13 encoding and SVG geometry deterministic.
* Use the nominal GS1 layout constants declared in `tool.py`.
* Reject invalid ISBN check digits instead of silently correcting them.
* Do not infer ISBN hyphenation; preserve caller-supplied `display_text` after
  confirming that it represents the encoded ISBN.
* Validate all inputs before writing and do not overwrite files unless the
  caller explicitly sets `overwrite` to `true`.
* Keep the implementation dependency-free and covered by known-vector tests.
