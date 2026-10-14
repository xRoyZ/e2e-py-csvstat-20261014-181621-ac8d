"""JSON rendering (stub).

The signature is final; the body is implemented by the ticket
"Implement the JSON output for --json".
"""

from .model import Report


def render_json(report: Report) -> str:
    """Render ``report`` as a JSON document."""
    return ""
