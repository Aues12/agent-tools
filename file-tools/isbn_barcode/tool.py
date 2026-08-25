"""Deterministic ISBN-13 / EAN-13 SVG generation and verification."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from html import escape
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


X_MM = 0.33
SYMBOL_MODULES = 95
LEFT_QUIET_MODULES = 11
RIGHT_QUIET_MODULES = 7
BAR_HEIGHT_MM = 22.85
GUARD_EXTENSION_MODULES = 5

TITLE_BASELINE_MM = 3.5
BAR_TOP_MM = 5.0
HRI_BASELINE_MM = BAR_TOP_MM + BAR_HEIGHT_MM + 2.85
BOTTOM_MARGIN_MM = 0.8

TOTAL_WIDTH_MM = round(
    (LEFT_QUIET_MODULES + SYMBOL_MODULES + RIGHT_QUIET_MODULES) * X_MM,
    3,
)
TOTAL_HEIGHT_MM = round(HRI_BASELINE_MM + BOTTOM_MARGIN_MM, 3)
SYMBOL_START_MM = LEFT_QUIET_MODULES * X_MM

LEFT_PATTERNS = (
    "LLLLLL",
    "LLGLGG",
    "LLGGLG",
    "LLGGGL",
    "LGLLGG",
    "LGGLLG",
    "LGGGLL",
    "LGLGLG",
    "LGLGGL",
    "LGGLGL",
)
L_CODES = (
    "0001101",
    "0011001",
    "0010011",
    "0111101",
    "0100011",
    "0110001",
    "0101111",
    "0111011",
    "0110111",
    "0001011",
)
R_CODES = tuple(
    "".join("1" if bit == "0" else "0" for bit in code) for code in L_CODES
)
G_CODES = tuple(code[::-1] for code in R_CODES)
GUARD_MODULES = frozenset((0, 2, 46, 48, 92, 94))
_OPS = {"generate_svg", "write_svg", "verify_svg"}


def normalize_isbn(value: str) -> str:
    """Remove an optional ISBN label, whitespace, and hyphens."""
    if not isinstance(value, str):
        raise TypeError("isbn must be a string")
    value = re.sub(r"^\s*ISBN(?:-13)?\s*:?\s*", "", value, flags=re.IGNORECASE)
    return re.sub(r"[-\s]", "", value)


def calculate_check_digit(first_twelve_digits: str) -> str:
    """Calculate an EAN-13 check digit from the first twelve digits."""
    if not isinstance(first_twelve_digits, str):
        raise TypeError("first_twelve_digits must be a string")
    if len(first_twelve_digits) != 12 or not first_twelve_digits.isdigit():
        raise ValueError("check-digit input must contain exactly 12 digits")
    weighted_sum = sum(
        int(digit) * (1 if index % 2 == 0 else 3)
        for index, digit in enumerate(first_twelve_digits)
    )
    return str((-weighted_sum) % 10)


def validate_isbn13(value: str) -> str:
    """Normalize and validate an ISBN-13 value without correcting it."""
    isbn = normalize_isbn(value)
    if len(isbn) != 13 or not isbn.isdigit():
        raise ValueError("ISBN-13 must contain exactly 13 digits")
    if not isbn.startswith(("978", "979")):
        raise ValueError("ISBN-13 must start with 978 or 979")
    expected = calculate_check_digit(isbn[:12])
    if isbn[-1] != expected:
        raise ValueError(
            f"invalid ISBN-13 check digit: expected {expected}, received {isbn[-1]}"
        )
    return isbn


def validate_display_text(display_text: str | None, isbn: str) -> str:
    """Validate the optional publication label against the encoded ISBN."""
    if display_text is None:
        return f"ISBN {isbn}"
    if not isinstance(display_text, str):
        raise TypeError("display_text must be a string or null")
    normalized_display = display_text.strip()
    if not re.match(r"^ISBN(?:-13)?\s", normalized_display, flags=re.IGNORECASE):
        raise ValueError("display_text must start with 'ISBN ' or 'ISBN-13 '")
    if normalize_isbn(normalized_display) != isbn:
        raise ValueError("display_text digits must match the encoded ISBN")
    return normalized_display


def encode_ean13(isbn: str) -> str:
    """Encode a validated ISBN as the 95-module EAN-13 bit pattern."""
    isbn = validate_isbn13(isbn)
    parity = LEFT_PATTERNS[int(isbn[0])]
    left = "".join(
        (L_CODES if encoding == "L" else G_CODES)[int(digit)]
        for digit, encoding in zip(isbn[1:7], parity)
    )
    right = "".join(R_CODES[int(digit)] for digit in isbn[7:])
    pattern = f"101{left}01010{right}101"
    if len(pattern) != SYMBOL_MODULES:
        raise AssertionError("EAN-13 pattern must contain 95 modules")
    return pattern


def generate_svg(isbn: str, display_text: str | None = None) -> dict[str, Any]:
    """Generate SVG text and metadata without writing a file."""
    normalized_isbn = validate_isbn13(isbn)
    normalized_display = validate_display_text(display_text, normalized_isbn)
    svg = _build_svg(normalized_isbn, normalized_display)
    verification = _verify_root(
        ElementTree.fromstring(svg), normalized_isbn, normalized_display
    )
    if not verification["valid"]:
        raise AssertionError("generated SVG failed internal verification")
    return {
        "isbn": normalized_isbn,
        "display_text": normalized_display,
        "svg": svg,
        "width_mm": TOTAL_WIDTH_MM,
        "height_mm": TOTAL_HEIGHT_MM,
        "x_dimension_mm": X_MM,
        "module_count": SYMBOL_MODULES,
    }


def write_svg(
    isbn: str,
    output_path: str | Path,
    display_text: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Atomically write one verified SVG file."""
    path = _as_path(output_path)
    if path.suffix.lower() != ".svg":
        raise ValueError("output_path must end with .svg")
    if not isinstance(overwrite, bool):
        raise TypeError("overwrite must be a boolean")
    if not path.parent.exists():
        raise FileNotFoundError(f"output directory does not exist: {path.parent}")
    if path.exists() and not overwrite:
        raise FileExistsError(f"output file already exists: {path}")

    generated = generate_svg(isbn, display_text)
    _write_text_atomically(path, generated["svg"])
    verification = verify_svg(path, generated["isbn"], generated["display_text"])
    if not verification["valid"]:
        raise RuntimeError("written SVG failed verification")

    return {
        key: value for key, value in generated.items() if key != "svg"
    } | {"path": str(path), "verification": verification}


def verify_svg(
    path: str | Path,
    isbn: str,
    display_text: str | None = None,
) -> dict[str, Any]:
    """Verify SVG geometry, text, and encoded modules against an ISBN."""
    svg_path = _as_path(path)
    normalized_isbn = validate_isbn13(isbn)
    expected_display = (
        validate_display_text(display_text, normalized_isbn)
        if display_text is not None
        else None
    )
    try:
        root = ElementTree.parse(svg_path).getroot()
    except ElementTree.ParseError as exc:
        raise ValueError(f"invalid SVG XML: {exc}") from exc

    report = _verify_root(root, normalized_isbn, expected_display)
    report["path"] = str(svg_path)
    report["isbn"] = normalized_isbn
    return report


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute an isbn_barcode operation from a structured request payload."""
    try:
        operation, params = _parse_request(input_data)
        if operation == "generate_svg":
            result = generate_svg(
                isbn=params["isbn"],
                display_text=params.get("display_text"),
            )
            message = f"Generated ISBN-13 SVG for {result['isbn']}"
        elif operation == "write_svg":
            result = write_svg(
                isbn=params["isbn"],
                output_path=params["output_path"],
                display_text=params.get("display_text"),
                overwrite=params.get("overwrite", False),
            )
            message = f"Wrote and verified ISBN-13 SVG at {result['path']}"
        elif operation == "verify_svg":
            result = verify_svg(
                path=params["path"],
                isbn=params["isbn"],
                display_text=params.get("display_text"),
            )
            message = (
                "SVG verification passed"
                if result["valid"]
                else "SVG verification found errors"
            )
        else:
            raise ValueError(f"unknown operation: {operation}")

        return {
            "success": True,
            "message": message,
            "result": result,
            "meta": {"operation": operation},
        }
    except Exception as exc:
        return _error_envelope(exc)


def main() -> None:
    """Read stdin JSON, execute one operation, and print stdout JSON."""
    raw = sys.stdin.read().strip()
    if not raw:
        response = _error_envelope(ValueError("No input received"))
        print(json.dumps(response, ensure_ascii=False, indent=2))
        sys.exit(2)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        response = _error_envelope(ValueError(f"Invalid JSON: {exc.msg}"))
        print(json.dumps(response, ensure_ascii=False, indent=2))
        sys.exit(2)

    response = run(payload)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    sys.exit(0 if response.get("success") is True else 1)


def _build_svg(isbn: str, display_text: str) -> str:
    """Build SVG markup from already validated values."""
    pattern = encode_ean13(isbn)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            f'width="{_mm(TOTAL_WIDTH_MM)}mm" height="{_mm(TOTAL_HEIGHT_MM)}mm" '
            f'viewBox="0 0 {_mm(TOTAL_WIDTH_MM)} {_mm(TOTAL_HEIGHT_MM)}" '
            'role="img" aria-labelledby="title desc">'
        ),
        f'  <title id="title">{escape(display_text)} barcode</title>',
        (
            f'  <desc id="desc">ISBN {escape(isbn)} encoded as EAN-13; '
            'nominal X-dimension 0.33 mm.</desc>'
        ),
        (
            f'  <rect width="{_mm(TOTAL_WIDTH_MM)}" '
            f'height="{_mm(TOTAL_HEIGHT_MM)}" fill="#fff"/>'
        ),
        (
            f'  <text id="isbn-title" x="{_mm(TOTAL_WIDTH_MM / 2)}" '
            f'y="{_mm(TITLE_BASELINE_MM)}" text-anchor="middle" '
            'font-family="Arial, Helvetica, sans-serif" font-size="3.175">'
            f'{escape(display_text)}</text>'
        ),
        '  <g id="bars" fill="#000" shape-rendering="crispEdges">',
    ]

    for run_start, run_width in _black_runs(pattern):
        x = SYMBOL_START_MM + run_start * X_MM
        run_modules = range(run_start, run_start + run_width)
        is_guard = all(module in GUARD_MODULES for module in run_modules)
        height = BAR_HEIGHT_MM + (
            GUARD_EXTENSION_MODULES * X_MM if is_guard else 0
        )
        kind = "guard" if is_guard else "data"
        lines.append(
            f'    <rect class="{kind}" data-module="{run_start}" '
            f'x="{_mm(x)}" y="{_mm(BAR_TOP_MM)}" '
            f'width="{_mm(run_width * X_MM)}" height="{_mm(height)}"/>'
        )

    lines.extend(
        [
            "  </g>",
            (
                '  <g id="human-readable" fill="#000" '
                'font-family="OCR-B, OCRB, Arial, Helvetica, sans-serif" '
                'font-size="2.75" text-anchor="middle">'
            ),
            (
                f'    <text x="{_mm(SYMBOL_START_MM - 4 * X_MM)}" '
                f'y="{_mm(HRI_BASELINE_MM)}">{isbn[0]}</text>'
            ),
        ]
    )
    for index, digit in enumerate(isbn[1:7]):
        x = SYMBOL_START_MM + (6.5 + 7 * index) * X_MM
        lines.append(
            f'    <text x="{_mm(x)}" y="{_mm(HRI_BASELINE_MM)}">{digit}</text>'
        )
    for index, digit in enumerate(isbn[7:]):
        x = SYMBOL_START_MM + (53.5 + 7 * index) * X_MM
        lines.append(
            f'    <text x="{_mm(x)}" y="{_mm(HRI_BASELINE_MM)}">{digit}</text>'
        )
    lines.extend(["  </g>", "</svg>", ""])
    return "\n".join(lines)


def _verify_root(
    root: ElementTree.Element,
    expected_isbn: str,
    expected_display: str | None,
) -> dict[str, Any]:
    """Return deterministic validation errors for a parsed SVG root."""
    ns = {"svg": "http://www.w3.org/2000/svg"}
    errors: list[str] = []
    expected_tag = "{http://www.w3.org/2000/svg}svg"
    if root.tag != expected_tag:
        errors.append("root element is not an SVG element")
    if root.get("width") != f"{_mm(TOTAL_WIDTH_MM)}mm":
        errors.append("width is not the nominal 113-module width")
    if root.get("height") != f"{_mm(TOTAL_HEIGHT_MM)}mm":
        errors.append("height does not match the publication layout")
    if root.get("viewBox") != f"0 0 {_mm(TOTAL_WIDTH_MM)} {_mm(TOTAL_HEIGHT_MM)}":
        errors.append("viewBox does not match physical dimensions")

    title = root.find(".//svg:text[@id='isbn-title']", ns)
    if title is None or not title.text:
        errors.append("ISBN title text is missing")
    else:
        try:
            if normalize_isbn(title.text) != expected_isbn:
                errors.append("ISBN title digits do not match the expected ISBN")
        except (TypeError, ValueError):
            errors.append("ISBN title is malformed")
        if expected_display is not None and title.text != expected_display:
            errors.append("ISBN title does not match display_text")

    bars = root.findall(".//svg:g[@id='bars']/svg:rect", ns)
    reconstructed = ["0"] * SYMBOL_MODULES
    guard_count = 0
    for bar in bars:
        try:
            start = int(bar.attrib["data-module"])
            width = float(bar.attrib["width"])
            x = float(bar.attrib["x"])
            y = float(bar.attrib["y"])
            height = float(bar.attrib["height"])
        except (KeyError, TypeError, ValueError):
            errors.append("a bar has missing or invalid geometry")
            continue

        module_width = width / X_MM
        modules = round(module_width)
        if modules < 1 or abs(module_width - modules) > 0.001:
            errors.append("a bar width is not an integer number of modules")
            continue
        if abs(x - (SYMBOL_START_MM + start * X_MM)) > 0.001:
            errors.append("a bar x-position does not match its module index")
        if abs(y - BAR_TOP_MM) > 0.001:
            errors.append("a bar y-position does not match the layout")

        run_modules = range(start, start + modules)
        is_guard = all(module in GUARD_MODULES for module in run_modules)
        expected_class = "guard" if is_guard else "data"
        expected_height = BAR_HEIGHT_MM + (
            GUARD_EXTENSION_MODULES * X_MM if is_guard else 0
        )
        if bar.get("class") != expected_class:
            errors.append("a bar has an incorrect guard/data class")
        if is_guard:
            guard_count += 1
        if abs(height - expected_height) > 0.001:
            errors.append("a bar height does not match its class")

        for module in run_modules:
            if not 0 <= module < SYMBOL_MODULES:
                errors.append("a bar extends outside the 95-module symbol")
            elif reconstructed[module] == "1":
                errors.append("bar modules overlap")
            else:
                reconstructed[module] = "1"

    if "".join(reconstructed) != encode_ean13(expected_isbn):
        errors.append("bar modules do not encode the expected ISBN")
    if guard_count != len(GUARD_MODULES):
        errors.append("the six guard bars are not all present")

    hri = root.findall(".//svg:g[@id='human-readable']/svg:text", ns)
    if "".join(text.text or "" for text in hri) != expected_isbn:
        errors.append("human-readable digits do not match the expected ISBN")

    return {
        "valid": not errors,
        "errors": errors,
        "checks": {
            "module_count": SYMBOL_MODULES,
            "guard_bar_count": guard_count,
            "width_mm": TOTAL_WIDTH_MM,
            "height_mm": TOTAL_HEIGHT_MM,
            "x_dimension_mm": X_MM,
        },
    }


def _black_runs(pattern: str) -> list[tuple[int, int]]:
    """Convert black modules into start/width runs."""
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for index, bit in enumerate(pattern + "0"):
        if bit == "1" and start is None:
            start = index
        elif bit == "0" and start is not None:
            runs.append((start, index - start))
            start = None
    return runs


def _mm(value: float) -> str:
    """Format millimetres without insignificant trailing zeroes."""
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _as_path(path: str | Path) -> Path:
    if isinstance(path, Path):
        return path
    if not isinstance(path, str):
        raise TypeError("path must be a string or Path")
    return Path(path)


def _write_text_atomically(path: Path, content: str) -> None:
    """Write UTF-8 text through a temporary sibling and replace the target."""
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _parse_request(input_data: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")
    operation = input_data.get("operation")
    if not isinstance(operation, str) or not operation:
        raise ValueError("operation must be a non-empty string")
    if operation not in _OPS:
        raise ValueError(f"unknown operation: {operation}")

    params = input_data.get("params")
    if params is None:
        params = {
            key: value
            for key, value in input_data.items()
            if key not in {"operation", "params", "meta"}
        }
    if not isinstance(params, dict):
        raise TypeError("params must be a dictionary")

    allowed = {
        "generate_svg": {"isbn", "display_text"},
        "write_svg": {"isbn", "output_path", "display_text", "overwrite"},
        "verify_svg": {"path", "isbn", "display_text"},
    }[operation]
    unexpected = set(params) - allowed
    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ValueError(f"unexpected parameter(s) for {operation}: {names}")

    required = {
        "generate_svg": {"isbn"},
        "write_svg": {"isbn", "output_path"},
        "verify_svg": {"path", "isbn"},
    }[operation]
    missing = required - set(params)
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"{operation} requires: {names}")
    return operation, params


def _error_envelope(exc: Exception) -> dict[str, Any]:
    message = str(exc)
    return {
        "success": False,
        "message": message,
        "error": {"type": exc.__class__.__name__, "message": message},
    }


if __name__ == "__main__":
    main()
