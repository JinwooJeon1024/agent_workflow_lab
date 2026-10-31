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


def format_ranges(values: Iterable[int]) -> str:
    """Render ranges as comma-separated single integers or start-end pairs."""
    return ",".join(
        str(start) if start == end else f"{start}-{end}"
        for start, end in coalesce_ranges(values)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("values", nargs="*", type=int, help="integers to summarize")
    args = parser.parse_args()
    print(json.dumps(coalesce_ranges(args.values)))


if __name__ == "__main__":
    main()
