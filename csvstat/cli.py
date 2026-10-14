"""Command line entry point for csvstat.

This module is complete and final: it wires the pipeline together and turns the
pipeline's errors into a ``csvstat: <message>`` line on stderr with the matching
exit code. The individual steps are implemented by their own tickets.
"""

import argparse
import sys

from .analyze import build_report
from .errors import CsvstatError
from .reader import normalize_delimiter, read_table
from .render_json import render_json
from .render_table import render_table


def _split_columns(value: str) -> list[str]:
    """Turn a ``--columns a,b,c`` value into a list of column names."""
    return value.split(",")


def build_parser() -> argparse.ArgumentParser:
    """Build the ``csvstat`` argument parser."""
    parser = argparse.ArgumentParser(
        prog="csvstat",
        description="Print per-column statistics for a CSV file.",
    )
    parser.add_argument("path", metavar="file", help="the CSV file to analyze")
    parser.add_argument(
        "--delimiter",
        default=",",
        metavar="CHAR",
        help="field delimiter of the input file (default: ',')",
    )
    parser.add_argument(
        "--columns",
        default=None,
        metavar="a,b,c",
        type=_split_columns,
        help="comma-separated list of columns to report, in this order",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the report as JSON instead of a table",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the csvstat pipeline and return the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        delimiter = normalize_delimiter(args.delimiter)
        table = read_table(args.path, delimiter)
        report = build_report(args.path, table, args.columns)
        text = render_json(report) if args.json else render_table(report)
    except CsvstatError as exc:
        print(f"csvstat: {exc}", file=sys.stderr)
        return exc.exit_code
    print(text)
    return 0
