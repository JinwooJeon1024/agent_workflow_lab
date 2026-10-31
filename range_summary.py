"""Summarize integers as sorted, maximal inclusive ranges."""

import argparse
from collections.abc import Iterable
import json


def coalesce_ranges(values: Iterable[int]) -> list[tuple[int, int]]:
    """Group distinct built-in integers into consecutive inclusive ranges."""
    unique = set()
    for value in values:
        if type(value) is not int:
            raise TypeError("values must contain only built-in integers")
        unique.add(value)

    ordered = sorted(unique)
    if not ordered:
        return []

    ranges = []
    start = end = ordered[0]
    for value in ordered[1:]:
        if value == end + 1:
            end = value
        else:
            ranges.append((start, end))
            start = end = value
    ranges.append((start, end))
    return ranges


def _format_integer(value: int) -> str:
    """Render an integer without changing Python's global digit limit."""
    try:
        return str(value)
    except ValueError:
        # Each chunk stays below the interpreter's decimal conversion limit.
        sign = "-" if value < 0 else ""
        value = abs(value)
        chunks = []
        while value >= 10**9:
            value, remainder = divmod(value, 10**9)
            chunks.append(f"{remainder:09d}")
        return sign + str(value) + "".join(reversed(chunks))


def format_ranges(values: Iterable[int]) -> str:
    """Render ranges as comma-separated single integers or start-end pairs."""
    return ",".join(
        _format_integer(start) if start == end
        else f"{_format_integer(start)}-{_format_integer(end)}"
        for start, end in coalesce_ranges(values)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("values", nargs="*", type=int, help="integers to summarize")
    args = parser.parse_args()
    print(json.dumps(coalesce_ranges(args.values)))


if __name__ == "__main__":
    main()
