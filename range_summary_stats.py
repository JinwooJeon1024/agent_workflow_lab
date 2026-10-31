"""Compute integer statistics from maximal inclusive ranges."""

from collections.abc import Iterable

from range_summary import coalesce_ranges


def summarize_ranges(values: Iterable[int]) -> dict[str, int]:
    """Count distinct built-in integers and ranges without expanding ranges.

    Input validation and single-pass consumption follow ``coalesce_ranges``.
    """
    ranges = coalesce_ranges(values)
    return {
        "value_count": sum(end - start + 1 for start, end in ranges),
        "range_count": len(ranges),
    }
