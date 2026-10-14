"""Per-column analysis (stub).

The signature is final; the body is implemented by the ticket
"Implement per-column statistics and type detection".
"""

from .model import Report, Table


def build_report(filename: str, table: Table, wanted: list[str] | None) -> Report:
    """Build the statistics report for ``table``."""
    return Report(filename, 0, [])
