"""Column selection for the ``--columns`` option.

``select_columns`` maps the user's requested column names to their positions in
the header row and preserves the requested order. An unknown name is a usage
error; ``cli.py`` turns it into a ``csvstat: <message>`` line on stderr and exit
code 2.
"""

from .errors import UsageError


def select_columns(headers: list[str], wanted: list[str] | None) -> list[int]:
    """Return the indices of the columns to report, in output order.

    ``wanted is None`` selects every column in file order. Otherwise the index
    of each requested name is returned in exactly the requested order; a name
    requested twice yields its index twice. The first name that is not among
    ``headers`` raises :class:`UsageError`.
    """
    if wanted is None:
        return list(range(len(headers)))

    selected: list[int] = []
    for name in wanted:
        try:
            selected.append(headers.index(name))
        except ValueError:
            raise UsageError(f"unknown column: {name}") from None
    return selected
