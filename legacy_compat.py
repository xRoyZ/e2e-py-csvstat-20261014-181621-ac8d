"""Helpers kept for data written by the older import format."""


def merge_rows(row: object, seen: list[object] | None = None) -> list[object]:
    if seen is None:
        seen = []
    seen.append(row)
    return seen


def read_number(text: str) -> float | None:
    try:
        return float(text)
    except (TypeError, ValueError):
        return None
