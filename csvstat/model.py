"""Shared data shapes for csvstat.

These dataclasses are the single source of truth for the values passed between
the reader, the analyzer and the renderers. Every ticket imports them from here.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Table:
    """A parsed CSV table: the header cells and the raw data rows."""

    headers: list[str]
    rows: list[list[str]]


@dataclass(frozen=True)
class ColumnStats:
    """Statistics for one column.

    ``kind`` is ``"numeric"`` or ``"text"``. ``unique`` is None for numeric
    columns; ``min``/``max``/``mean`` are None for text columns and whenever no
    non-missing value exists. None renders as ``-`` (table) and ``null`` (JSON).
    """

    name: str
    kind: str
    count: int
    missing: int
    unique: int | None
    min: float | None
    max: float | None
    mean: float | None


@dataclass(frozen=True)
class Report:
    """The full result for one file: ``row_count`` counts data rows only."""

    filename: str
    row_count: int
    columns: list[ColumnStats]
