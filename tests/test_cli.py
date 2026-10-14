"""CLI skeleton tests.

These cover only what the skeleton itself delivers: the argument surface that
``--help`` advertises, the argparse usage path for a bad option, and that the
wired pipeline runs to completion on a valid input file. Nothing here asserts
the behaviour of the reader, the analysis or the renderers - those belong to
their own tickets and their own test files.
"""

from pathlib import Path

import pytest

from csvstat.cli import main


def test_help_exits_zero_and_names_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "file" in out
    assert "--delimiter" in out
    assert "--columns" in out
    assert "--json" in out


def test_unknown_option_exits_two_with_usage_on_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--not-an-option", "file.csv"])
    assert excinfo.value.code == 2
    err = capsys.readouterr().err
    assert "usage" in err.lower()


def test_main_returns_zero_for_a_valid_file(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("name,age\nAda,36\n", encoding="utf-8")
    assert main([str(csv_file)]) == 0
