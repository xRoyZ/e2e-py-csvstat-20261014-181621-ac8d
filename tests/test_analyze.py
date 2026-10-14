"""Tests for :func:`csvstat.analyze.build_report`.

The tests cover the statistics of numeric and text columns, missing-value
handling, type detection through ``int()``/``float()`` only, header-only files
and the pass-through of the requested column order.
"""

import pytest

from csvstat import analyze
from csvstat.model import Table


@pytest.fixture(autouse=True)
def selection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide the ``select_columns`` behaviour ``build_report`` relies on.

    ``select_columns`` belongs to its own ticket and is still a stub on this
    branch, so the analyze tests inject the agreed contract: ``None`` selects
    every column in header order, a list selects exactly those columns in that
    order. ``build_report`` still calls the real name at runtime.
    """

    def select(headers: list[str], wanted: list[str] | None) -> list[int]:
        if wanted is None:
            return list(range(len(headers)))
        return [headers.index(name) for name in wanted]

    monkeypatch.setattr(analyze, "select_columns", select)


def test_numeric_int_column() -> None:
    table = Table(["age"], [["1"], ["2"], ["3"]])
    report = analyze.build_report("data.csv", table, None)

    assert report.filename == "data.csv"
    assert report.row_count == 3
    (column,) = report.columns
    assert column.name == "age"
    assert column.kind == "numeric"
    assert column.count == 3
    assert column.missing == 0
    assert column.unique is None
    assert column.min == 1.0
    assert column.max == 3.0
    assert column.mean == pytest.approx(2.0)


def test_numeric_float_column() -> None:
    table = Table(["x"], [["1.5"], ["2.5"], ["3"]])
    (column,) = analyze.build_report("data.csv", table, None).columns

    assert column.kind == "numeric"
    assert column.count == 3
    assert column.min == 1.5
    assert column.max == 3.0
    assert column.mean == pytest.approx(7.0 / 3.0)


def test_negative_values() -> None:
    table = Table(["v"], [["-5"], ["-1.5"], ["3"]])
    (column,) = analyze.build_report("data.csv", table, None).columns

    assert column.kind == "numeric"
    assert column.min == -5.0
    assert column.max == 3.0
    assert column.mean == pytest.approx((-5.0 - 1.5 + 3.0) / 3.0)


def test_number_mixed_with_non_number_is_text() -> None:
    table = Table(["v"], [["10"], ["oops"], ["30"]])
    (column,) = analyze.build_report("data.csv", table, None).columns

    assert column.kind == "text"
    assert column.count == 3
    assert column.missing == 0
    assert column.unique == 3
    assert column.min is None
    assert column.max is None
    assert column.mean is None


def test_empty_and_whitespace_cells_are_missing() -> None:
    table = Table(["v"], [["1"], [""], ["   "], ["2"]])
    (column,) = analyze.build_report("data.csv", table, None).columns

    assert column.kind == "numeric"
    assert column.missing == 2
    assert column.count == 2
    assert column.min == 1.0
    assert column.max == 2.0
    assert column.mean == pytest.approx(1.5)


def test_missing_values_do_not_change_text_unique_count() -> None:
    table = Table(["name"], [["Ada"], [""], ["   "], ["Bob"]])
    (column,) = analyze.build_report("data.csv", table, None).columns

    assert column.kind == "text"
    assert column.count == 2
    assert column.missing == 2
    assert column.unique == 2


def test_expression_like_cell_is_text_and_never_executed() -> None:
    table = Table(["v"], [["2+2"], ['__import__("os")']])
    (column,) = analyze.build_report("data.csv", table, None).columns

    assert column.kind == "text"
    assert column.count == 2
    assert column.unique == 2
    assert column.min is None
    assert column.max is None
    assert column.mean is None


def test_header_only_file_yields_empty_text_columns() -> None:
    table = Table(["a", "b"], [])
    report = analyze.build_report("empty.csv", table, None)

    assert report.row_count == 0
    assert [column.name for column in report.columns] == ["a", "b"]
    for column in report.columns:
        assert column.kind == "text"
        assert column.count == 0
        assert column.missing == 0
        assert column.unique == 0
        assert column.min is None
        assert column.max is None
        assert column.mean is None


def test_column_without_non_missing_values() -> None:
    table = Table(["v"], [[""], ["   "]])
    (column,) = analyze.build_report("data.csv", table, None).columns

    assert column.kind == "text"
    assert column.count == 0
    assert column.missing == 2
    assert column.unique == 0
    assert column.min is None
    assert column.max is None
    assert column.mean is None


def test_wanted_none_keeps_header_order() -> None:
    table = Table(["a", "b", "c"], [["1", "2", "3"]])
    report = analyze.build_report("data.csv", table, None)

    assert [column.name for column in report.columns] == ["a", "b", "c"]


def test_reordered_wanted_controls_output_order() -> None:
    table = Table(["a", "b", "c"], [["1", "text", "3"]])
    report = analyze.build_report("data.csv", table, ["c", "a"])

    assert [column.name for column in report.columns] == ["c", "a"]
    assert report.columns[0].kind == "numeric"
    assert report.columns[1].kind == "numeric"


def test_build_report_forwards_request_to_select_columns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    def recording_select(headers: list[str], wanted: list[str] | None) -> list[int]:
        seen["headers"] = headers
        seen["wanted"] = wanted
        return [1]

    monkeypatch.setattr(analyze, "select_columns", recording_select)
    table = Table(["a", "b"], [["1", "2"]])
    report = analyze.build_report("data.csv", table, ["b"])

    assert seen["headers"] == ["a", "b"]
    assert seen["wanted"] == ["b"]
    assert [column.name for column in report.columns] == ["b"]


def test_row_count_counts_data_rows_only() -> None:
    table = Table(["a"], [["1"], ["2"], ["3"], ["4"]])
    assert analyze.build_report("data.csv", table, None).row_count == 4
