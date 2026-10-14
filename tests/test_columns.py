"""Tests for ``--columns`` selection and ordering (``csvstat.columns``).

The unit tests drive ``select_columns`` directly. The two CLI tests exercise the
real ``csvstat.cli.main`` path on a temporary CSV; because the reader, analyzer
and renderers are still stubs on this branch, the test injects a minimal
pipeline that keeps the real ``select_columns`` in the loop, so the CLI's
argument parsing, ordering and error propagation are what is under test.
"""

import csv as csv_module
from pathlib import Path

import pytest

from csvstat import cli
from csvstat.columns import select_columns
from csvstat.errors import UsageError
from csvstat.model import ColumnStats, Report, Table


def _install_minimal_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wire a real-enough pipeline so the CLI reaches ``select_columns``."""

    def fake_read_table(path: str, delimiter: str) -> Table:
        separator = delimiter if len(delimiter) == 1 else ","
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv_module.reader(handle, delimiter=separator))
        if not rows:
            return Table([], [])
        return Table(rows[0], rows[1:])

    def fake_build_report(filename: str, table: Table, wanted: list[str] | None) -> Report:
        indices = select_columns(table.headers, wanted)
        columns = [
            ColumnStats(table.headers[index], "text", 0, 0, 0, None, None, None)
            for index in indices
        ]
        return Report(filename, len(table.rows), columns)

    def fake_render_table(report: Report) -> str:
        return "\n".join(column.name for column in report.columns)

    monkeypatch.setattr(cli, "read_table", fake_read_table)
    monkeypatch.setattr(cli, "build_report", fake_build_report)
    monkeypatch.setattr(cli, "render_table", fake_render_table)


def test_default_selects_every_column_in_file_order() -> None:
    assert select_columns(["a", "b", "c"], None) == [0, 1, 2]


def test_select_columns_reorders_to_requested_order() -> None:
    assert select_columns(["a", "b"], ["b", "a"]) == [1, 0]


def test_select_columns_duplicate_name_yields_index_twice() -> None:
    assert select_columns(["a", "b"], ["b", "b", "a"]) == [1, 1, 0]


def test_select_columns_unknown_name_raises_usage_error() -> None:
    with pytest.raises(UsageError) as excinfo:
        select_columns(["a", "b"], ["a", "zzz"])
    assert "zzz" in str(excinfo.value)


def test_select_columns_names_the_first_unknown_column() -> None:
    with pytest.raises(UsageError) as excinfo:
        select_columns(["a", "b"], ["b", "first_missing", "second_missing"])
    message = str(excinfo.value)
    assert "first_missing" in message
    assert "second_missing" not in message


def test_select_columns_wrong_case_is_unknown() -> None:
    with pytest.raises(UsageError):
        select_columns(["a", "b"], ["B"])


def test_select_columns_blank_name_is_unknown() -> None:
    with pytest.raises(UsageError):
        select_columns(["a", "b"], ["a", " "])


def test_cli_columns_prints_columns_in_requested_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b,c\n1,2,3\n", encoding="utf-8")
    _install_minimal_pipeline(monkeypatch)

    assert cli.main([str(csv_file), "--columns", "b,a"]) == 0
    out = capsys.readouterr().out
    assert out.splitlines() == ["b", "a"]


def test_cli_unknown_column_reports_usage_error_and_exits_two(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("a,b\n1,2\n", encoding="utf-8")
    _install_minimal_pipeline(monkeypatch)

    assert cli.main([str(csv_file), "--columns", "b,missing"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("csvstat: ")
    assert "missing" in captured.err
    assert "Traceback" not in captured.err
