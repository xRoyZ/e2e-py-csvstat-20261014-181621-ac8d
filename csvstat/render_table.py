"""Fixed-width table rendering for csvstat.

The table prints one header line and one row per column of the report. Text that
originates in the CSV (column names and the file name) is passed through
:func:`sanitize` first, so a cell value can never contain a control character
that moves the cursor or changes the terminal colours.
"""

from .model import Report

_HEADERS = ["name", "kind", "count", "min", "max", "mean", "missing", "unique"]
_LEFT_ALIGNED = {0, 1}


def sanitize(text: str) -> str:
    """Return ``text`` with control characters made harmless.

    ESC (0x1B) starts a terminal escape sequence and could move the cursor or
    change colours, so it is replaced with a visible ``\\x1b``. Every other C0
    control character and DEL becomes a space so it cannot break the layout.
    Printable characters are left untouched.
    """
    out: list[str] = []
    for char in text:
        code = ord(char)
        if char == "\x1b":
            out.append("\\x1b")
        elif code < 0x20 or code == 0x7F:
            out.append(" ")
        else:
            out.append(char)
    return "".join(out)


def _format_number(value: float | None) -> str:
    """Format a numeric figure, or ``-`` when it does not exist."""
    return "-" if value is None else f"{value:g}"


def _format_optional_int(value: int | None) -> str:
    """Format a count that may not exist, or ``-``."""
    return "-" if value is None else str(value)


def render_table(report: Report) -> str:
    """Render ``report`` as a human readable fixed-width table."""
    rows: list[list[str]] = []
    for column in report.columns:
        rows.append(
            [
                sanitize(column.name),
                column.kind,
                str(column.count),
                _format_number(column.min),
                _format_number(column.max),
                _format_number(column.mean),
                str(column.missing),
                _format_optional_int(column.unique),
            ]
        )

    all_rows = [_HEADERS, *rows]
    widths = [max(len(row[i]) for row in all_rows) for i in range(len(_HEADERS))]

    lines = [f"file: {sanitize(report.filename)} ({report.row_count} rows)"]
    for row in all_rows:
        cells = [
            cell.ljust(widths[i]) if i in _LEFT_ALIGNED else cell.rjust(widths[i])
            for i, cell in enumerate(row)
        ]
        lines.append("  ".join(cells).rstrip())
    return "\n".join(lines)
