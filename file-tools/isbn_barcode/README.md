# isbn_barcode

Generate and verify dependency-free ISBN-13 barcodes as publication-layout
EAN-13 SVG files.

The generated symbol uses the nominal GS1 geometry: a 0.33 mm X-dimension,
95 symbol modules, 11X/7X quiet zones, 22.85 mm data bars, and guard bars
extended downward by 5X. The ISBN label is placed above the symbol and all 13
human-readable digits are positioned below it.

ISBN registrant and publication ranges cannot be inferred safely without the
official range data. Pass the assigned hyphenation through `display_text`; when
omitted, the title uses an unhyphenated ISBN. The tool always checks that title
digits match the encoded value.

## JSON CLI

```bash
printf '%s' '{
  "operation": "write_svg",
  "params": {
    "isbn": "9786253798338",
    "display_text": "ISBN 978-625-379-833-8",
    "output_path": "/tmp/isbn-9786253798338.svg"
  }
}' | python3 file-tools/isbn_barcode/isbn_barcode.py
```

Verify an existing file:

```bash
printf '%s' '{
  "operation": "verify_svg",
  "params": {
    "path": "/tmp/isbn-9786253798338.svg",
    "isbn": "9786253798338"
  }
}' | python3 file-tools/isbn_barcode/isbn_barcode.py
```

## Python API

```python
from tool import generate_svg, verify_svg, write_svg

generated = generate_svg("9786253798338", "ISBN 978-625-379-833-8")
written = write_svg(
    "9786253798338",
    "/tmp/isbn-9786253798338.svg",
    "ISBN 978-625-379-833-8",
)
report = verify_svg(written["path"], written["isbn"])
```

`write_svg` refuses to replace an existing file unless `overwrite=True` is
explicitly supplied.
