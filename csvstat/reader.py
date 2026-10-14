"""CSV reading and delimiter handling (stub).

The signatures are final; the bodies are implemented by the ticket
"Implement robust CSV reading and delimiter handling".
"""

from .model import Table


def normalize_delimiter(raw: str) -> str:
    """Return the delimiter to use for a user supplied ``--delimiter`` value."""
    return ""


def read_table(path: str, delimiter: str) -> Table:
    """Read the CSV at ``path`` into a Table."""
    return Table([], [])
