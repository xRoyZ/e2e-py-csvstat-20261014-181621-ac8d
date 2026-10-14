"""CSV reading and delimiter handling.

Two responsibilities live here:

* :func:`normalize_delimiter` turns the user supplied ``--delimiter`` value into
  the single character the ``csv`` module expects (with the two-character
  sequence ``\\t`` meaning a real tab).
* :func:`read_table` reads a CSV file into a :class:`~csvstat.model.Table`,
  reporting every file/read problem as an ``InputError`` whose message names the
  file and the cause only.
"""

import csv
import os

from .errors import InputError, UsageError
from .model import Table

_TAB_ESCAPE = "\\t"


def normalize_delimiter(raw: str) -> str:
    """Return the delimiter to use for a user supplied ``--delimiter`` value.

    The two-character sequence ``\\t`` becomes a real tab, any other string of
    exactly one character is returned unchanged, and anything else raises a
    :class:`~csvstat.errors.UsageError`.
    """
    if raw == _TAB_ESCAPE:
        return "\t"
    if len(raw) == 1:
        return raw
    raise UsageError("delimiter must be a single character or '\\t'")


def read_table(path: str, delimiter: str) -> Table:
    """Read the CSV at ``path`` into a :class:`~csvstat.model.Table`.

    The file is opened with ``encoding="utf-8-sig"`` (a byte-order mark is
    dropped) and ``newline=""`` (so CRLF line endings and quoted fields
    containing the delimiter are handled by the ``csv`` module). Cell strings
    are kept verbatim: no stripping and no type conversion.

    A missing, unreadable, empty or undecodable file raises an
    :class:`~csvstat.errors.InputError`.
    """
    try:
        size = os.path.getsize(path)
    except FileNotFoundError:
        raise InputError(f"cannot read {path}: file not found") from None
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc.strerror or 'read error'}") from None

    if size == 0:
        raise InputError(f"cannot read {path}: file is empty")

    try:
        with open(path, encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle, delimiter=delimiter))
    except UnicodeDecodeError:
        raise InputError(f"cannot read {path}: invalid UTF-8") from None
    except csv.Error as exc:
        raise InputError(f"cannot read {path}: {exc}") from None
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc.strerror or 'read error'}") from None

    if not rows:
        raise InputError(f"cannot read {path}: file is empty")

    headers = rows[0]
    return Table(headers, rows[1:])
