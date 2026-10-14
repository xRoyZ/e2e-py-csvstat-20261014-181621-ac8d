"""Tests for the fixed-width table renderer in ``csvstat.render_table``."""

import re

from csvstat.model import ColumnStats, Report
from csvstat.render_table import render_table

_SEPARATOR = re.compile(r"\s{2,}")


def _cells(line: str) -> list[str]:
    """Split one rendered line into its aligned cells."""
    return _SEPARATOR.split(line.strip())


def _report(*columns: ColumnStats, filename: str = "data.csv", rows: int = 2) -> Report:
    return Report(filename=filename, row_count=rows, columns=list(columns))


def test_two_column_report_aligns_the_columns() -> None:
    report = _report(
        ColumnStats("n", "numeric", 2, 0, None, 1.0, 3.0, 2.0),
        ColumnStats("word", "text", 2, 1, 1, None, None, None),
    )
    lines = render_table(report).splitlines()

    assert _cells(lines[1]) == ["name", "kind", "count", "min", "max", "mean", "missing", "unique"]

    data_rows = [_cells(line) for line in lines[2:]]
    assert len(data_rows) == 2
    for cells in data_rows:
        assert len(cells) == 8
    assert data_rows[0][0] == "n"
    assert data_rows[0][1] == "numeric"
    assert data_rows[1][0] == "word"
    assert data_rows[1][1] == "text"


def test_missing_figures_render_as_dash() -> None:
    text = ColumnStats("word", "text", 2, 1, 1, None, None, None)
    numeric = ColumnStats("n", "numeric", 2, 0, None, 1.0, 3.0, 2.0)
    lines = render_table(_report(text, numeric)).splitlines()

    text_cells = _cells(lines[2])
    assert text_cells[3] == "-"  # min
    assert text_cells[4] == "-"  # max
    assert text_cells[5] == "-"  # mean

    numeric_cells = _cells(lines[3])
    assert numeric_cells[7] == "-"  # unique does not exist for numeric columns
    assert numeric_cells[3] == "1"
    assert numeric_cells[4] == "3"


def test_text_column_shows_its_distinct_count() -> None:
    text = ColumnStats("word", "text", 3, 1, 2, None, None, None)
    lines = render_table(_report(text)).splitlines()

    assert _cells(lines[2])[7] == "2"


def test_control_characters_are_sanitized_but_figures_unchanged() -> None:
    report = _report(
        ColumnStats("na\x1b[31mme", "text", 1, 0, 1, None, None, None),
        filename="ev\x1bil.csv",
        rows=1,
    )
    out = render_table(report)

    assert "\x1b" not in out
    assert "\\x1b" in out

    lines = out.splitlines()
    cells = _cells(lines[2])
    assert cells[2] == "1"  # count changed by no control character
    assert cells[6] == "0"  # missing
    assert cells[7] == "1"  # unique
