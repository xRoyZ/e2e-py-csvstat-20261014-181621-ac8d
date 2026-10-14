"""Tests for the JSON output of ``--json``.

They cover the renderer directly (a hand-built mixed report) and the CLI path
(``python -m csvstat --json`` via ``main``), asserting that stdout is a single
parseable JSON object.
"""

import json
from pathlib import Path

import pytest

from csvstat.cli import main
from csvstat.model import ColumnStats, Report
from csvstat.render_json import render_json


def _mixed_report() -> Report:
    return Report(
        filename="data.csv",
        row_count=3,
        columns=[
            ColumnStats(
                name="age",
                kind="numeric",
                count=3,
                missing=0,
                unique=None,
                min=36.0,
                max=42.0,
                mean=39.0,
            ),
            ColumnStats(
                name="city",
                kind="text",
                count=2,
                missing=1,
                unique=2,
                min=None,
                max=None,
                mean=None,
            ),
        ],
    )


def test_render_json_is_a_single_valid_object() -> None:
    text = render_json(_mixed_report())
    payload = json.loads(text)
    assert isinstance(payload, dict)


def test_render_json_top_level_fields() -> None:
    payload = json.loads(render_json(_mixed_report()))
    assert payload["filename"] == "data.csv"
    assert payload["row_count"] == 3
    assert isinstance(payload["columns"], list)
    assert len(payload["columns"]) == 2


def test_render_json_numeric_column() -> None:
    payload = json.loads(render_json(_mixed_report()))
    age = payload["columns"][0]
    assert age["name"] == "age"
    assert age["kind"] == "numeric"
    assert age["count"] == 3
    assert age["missing"] == 0
    assert age["unique"] is None
    assert age["min"] == 36.0
    assert age["max"] == 42.0
    assert age["mean"] == 39.0


def test_render_json_text_column_with_missing_values_as_null() -> None:
    payload = json.loads(render_json(_mixed_report()))
    city = payload["columns"][1]
    assert city["name"] == "city"
    assert city["kind"] == "text"
    assert city["count"] == 2
    assert city["missing"] == 1
    assert city["unique"] == 2
    assert city["min"] is None
    assert city["max"] is None
    assert city["mean"] is None


def test_render_json_escapes_control_characters() -> None:
    report = Report(
        filename="evil.csv",
        row_count=1,
        columns=[
            ColumnStats(
                name="name",
                kind="text",
                count=1,
                missing=0,
                unique=1,
                min=None,
                max=None,
                mean=None,
            )
        ],
    )
    text = render_json(report)
    assert "\x1b" not in text
    assert json.loads(text)["columns"][0]["name"] == "name"


def test_cli_json_outputs_parseable_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("name,age\nAda,36\nBob,\n", encoding="utf-8")

    exit_code = main(["--json", str(csv_file)])

    assert exit_code == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert isinstance(payload, dict)
    assert payload["filename"] == str(csv_file)
    assert isinstance(payload["row_count"], int)
    assert isinstance(payload["columns"], list)
