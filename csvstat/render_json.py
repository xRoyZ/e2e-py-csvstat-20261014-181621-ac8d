"""JSON rendering of a Report.

``render_json`` turns the shared :class:`~csvstat.model.Report` into a single
JSON object. It returns the text; ``cli.py`` prints it on stdout.
"""

import json

from .model import ColumnStats, Report


def _column_to_dict(column: ColumnStats) -> dict[str, object]:
    """Return one column as a plain dict, ``None`` staying ``None`` (null)."""
    return {
        "name": column.name,
        "kind": column.kind,
        "count": column.count,
        "missing": column.missing,
        "unique": column.unique,
        "min": column.min,
        "max": column.max,
        "mean": column.mean,
    }


def render_json(report: Report) -> str:
    """Render ``report`` as a single JSON object.

    ``json.dumps`` both guarantees valid JSON and escapes any control character
    (such as a raw ESC from a CSV cell) as ``\\uXXXX``, so the text can never
    manipulate the terminal. Figures that are ``None`` are emitted as ``null``.
    """
    payload = {
        "filename": report.filename,
        "row_count": report.row_count,
        "columns": [_column_to_dict(column) for column in report.columns],
    }
    return json.dumps(payload)
