"""Error types for csvstat.

Only ``cli.py`` prints these; the analysis modules raise them and let the CLI
turn them into ``csvstat: <message>`` on stderr plus the matching exit code.
"""


class CsvstatError(Exception):
    """Base class for every expected csvstat failure."""

    exit_code: int = 1

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UsageError(CsvstatError):
    """A bad invocation (unknown column, bad option value). Exit code 2."""

    exit_code = 2


class InputError(CsvstatError):
    """A file or read problem. Exit code 1."""

    exit_code = 1
