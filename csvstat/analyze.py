"""Per-column statistics and type detection.

``build_report`` turns a parsed :class:`~csvstat.model.Table` into a
:class:`~csvstat.model.Report` with one :class:`~csvstat.model.ColumnStats` per
selected column. The column selection and its output order come from
:func:`csvstat.columns.select_columns`; this module computes the statistics.

A cell is *missing* when its ``strip()`` is empty. Missing cells count only into
``missing``; they never affect count, min, max, mean or unique. A column is
numeric when it has at least one non-missing value and every non-missing value
parses with ``int()`` followed by ``float()`` - never ``eval`` or ``exec``.
"""

from .columns import select_columns
from .model import ColumnStats, Report, Table


def _as_number(value: str) -> float | None:
    """Return ``value`` as a number, or ``None`` when it is not numeric.

    Parsing goes through ``int()`` first and ``float()`` second; no dynamic
    execution of the cell content ever happens, so a cell like ``2+2`` is text.
    """
    text = value.strip()
    try:
        return float(int(text))
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return None


def _numbers(values: list[str]) -> list[float] | None:
    """Parse every value as a number, or return ``None`` if any is not numeric."""
    parsed: list[float] = []
    for value in values:
        number = _as_number(value)
        if number is None:
            return None
        parsed.append(number)
    return parsed


def _column_stats(name: str, values: list[str]) -> ColumnStats:
    """Compute the statistics for one column from its verbatim cell values."""
    non_missing = [value for value in values if value.strip() != ""]
    missing = len(values) - len(non_missing)
    numbers = _numbers(non_missing) if non_missing else None
    if numbers is not None:
        return ColumnStats(
            name=name,
            kind="numeric",
            count=len(non_missing),
            missing=missing,
            unique=None,
            min=min(numbers),
            max=max(numbers),
            mean=sum(numbers) / len(numbers),
        )
    return ColumnStats(
        name=name,
        kind="text",
        count=len(non_missing),
        missing=missing,
        unique=len(set(non_missing)),
        min=None,
        max=None,
        mean=None,
    )


def build_report(filename: str, table: Table, wanted: list[str] | None) -> Report:
    """Build the statistics report for ``table``."""
    columns: list[ColumnStats] = []
    for index in select_columns(table.headers, wanted):
        values = [row[index] if index < len(row) else "" for row in table.rows]
        columns.append(_column_stats(table.headers[index], values))
    return Report(filename, len(table.rows), columns)
