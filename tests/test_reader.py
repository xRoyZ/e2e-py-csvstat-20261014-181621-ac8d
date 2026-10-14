"""Tests for csvstat.reader: delimiter handling and robust CSV reading.

The reader is exercised directly for the parsing behaviour and through the CLI
for the error paths, because the CLI is what turns the exceptions into the
``csvstat: <message>`` line on stderr and the exit code.
"""

from pathlib import Path

import pytest

from csvstat.cli import main
from csvstat.errors import InputError, UsageError
from csvstat.reader import normalize_delimiter, read_table


def test_normalize_delimiter_single_char() -> None:
    assert normalize_delimiter(";") == ";"
    assert normalize_delimiter(",") == ","
    assert normalize_delimiter("|") == "|"


def test_normalize_delimiter_tab_escape() -> None:
    assert normalize_delimiter("\\t") == "\t"


def test_normalize_delimiter_invalid_raises_usage_error() -> None:
    with pytest.raises(UsageError):
        normalize_delimiter(";;")
    with pytest.raises(UsageError):
        normalize_delimiter("")


def test_read_table_comma_default(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("name,age\nAda,36\nBob,41\n", encoding="utf-8")

    table = read_table(str(path), ",")

    assert table.headers == ["name", "age"]
    assert table.rows == [["Ada", "36"], ["Bob", "41"]]


def test_read_table_semicolon_delimiter(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("name;age\nAda;36\n", encoding="utf-8")

    table = read_table(str(path), normalize_delimiter(";"))

    assert table.headers == ["name", "age"]
    assert table.rows == [["Ada", "36"]]


def test_read_table_tab_delimiter(tmp_path: Path) -> None:
    path = tmp_path / "data.tsv"
    path.write_text("name\tage\nAda\t36\n", encoding="utf-8")

    table = read_table(str(path), normalize_delimiter("\\t"))

    assert table.headers == ["name", "age"]
    assert table.rows == [["Ada", "36"]]


def test_read_table_crlf_line_endings(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_bytes(b"name,age\r\nAda,36\r\nBob,41\r\n")

    table = read_table(str(path), ",")

    assert table.headers == ["name", "age"]
    assert table.rows == [["Ada", "36"], ["Bob", "41"]]


def test_read_table_drops_utf8_bom(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_bytes(b"\xef\xbb\xbfname,age\nAda,36\n")

    table = read_table(str(path), ",")

    assert table.headers == ["name", "age"]
    assert table.rows == [["Ada", "36"]]


def test_read_table_quoted_field_containing_comma(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_bytes(b'name,city\n"Ada, Lovelace",London\n')

    table = read_table(str(path), ",")

    assert table.headers == ["name", "city"]
    assert table.rows == [["Ada, Lovelace", "London"]]


def test_read_table_keeps_cells_verbatim(tmp_path: Path) -> None:
    path = tmp_path / "data.csv"
    path.write_text("a,b\n  x  ,\n", encoding="utf-8")

    table = read_table(str(path), ",")

    assert table.rows == [["  x  ", ""]]


def test_read_table_rejects_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_bytes(b"")

    with pytest.raises(InputError):
        read_table(str(path), ",")


def test_missing_file_cli_exit_one_message_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "nope.csv"

    code = main([str(missing)])
    captured = capsys.readouterr()

    assert code == 1
    assert captured.out == ""
    assert "csvstat:" in captured.err
    assert missing.name in captured.err
    assert "Traceback" not in captured.err


def test_zero_byte_file_cli_exit_one_message_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    empty = tmp_path / "empty.csv"
    empty.write_bytes(b"")

    code = main([str(empty)])
    captured = capsys.readouterr()

    assert code == 1
    assert "csvstat:" in captured.err
    assert empty.name in captured.err
    assert "Traceback" not in captured.err
