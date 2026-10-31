"""Acceptance tests for range statistics and the existing input contract."""

import itertools
import unittest
from unittest.mock import patch

from range_summary import coalesce_ranges
from range_summary_stats import summarize_ranges


class RangeStatsTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(summarize_ranges([]), {"value_count": 0, "range_count": 0})

    def test_unsorted_example_with_duplicates(self):
        self.assertEqual(
            summarize_ranges([3, 1, 2, 2, 6]),
            {"value_count": 4, "range_count": 2},
        )

    def test_example_crossing_zero(self):
        self.assertEqual(
            summarize_ranges([0, -2, -1, 4]),
            {"value_count": 4, "range_count": 2},
        )

    def test_single_value(self):
        self.assertEqual(summarize_ranges([7]), {"value_count": 1, "range_count": 1})

    def test_all_duplicates(self):
        self.assertEqual(
            summarize_ranges([5, 5, 5, 5]),
            {"value_count": 1, "range_count": 1},
        )

    def test_separated_values(self):
        self.assertEqual(
            summarize_ranges([9, 1, 5]),
            {"value_count": 3, "range_count": 3},
        )

    def test_negative_ranges(self):
        self.assertEqual(
            summarize_ranges([-4, -10, -3, -9, -10]),
            {"value_count": 4, "range_count": 2},
        )

    def test_arbitrary_size_integers_and_large_gaps(self):
        big = 10**100
        self.assertEqual(
            summarize_ranges([big + 1, -big, big, -big + 1, big]),
            {"value_count": 4, "range_count": 2},
        )

    def test_input_not_modified(self):
        values = [3, 1, 2, 2, 6]
        before = values.copy()
        self.assertEqual(
            summarize_ranges(values), {"value_count": 4, "range_count": 2}
        )
        self.assertEqual(values, before)

    def test_generator(self):
        values = (value for value in [4, 2, 3, 3, 8])
        self.assertEqual(
            summarize_ranges(values), {"value_count": 4, "range_count": 2}
        )
        self.assertEqual(list(values), [])

    def test_iterable_consumed_once(self):
        class SinglePassIterable:
            def __init__(self):
                self.iterations = 0

            def __iter__(self):
                self.iterations += 1
                if self.iterations != 1:
                    raise AssertionError("Input iterated more than once")
                yield from [3, 1, 2, 2, 6]

        values = SinglePassIterable()
        self.assertEqual(
            summarize_ranges(values), {"value_count": 4, "range_count": 2}
        )
        self.assertEqual(values.iterations, 1)

    def test_non_builtin_integer_elements_rejected(self):
        class IntegerSubclass(int):
            pass

        for invalid in (True, False, 1.0, "1", None, IntegerSubclass(1), [], {}):
            with self.subTest(element_type=type(invalid).__name__, value=repr(invalid)):
                with self.assertRaises(TypeError):
                    summarize_ranges(iter([1, invalid, 2]))

    def test_delegates_to_existing_coalescer_once(self):
        values = iter([3, 1, 2, 2, 6])
        with patch("range_summary_stats.coalesce_ranges", wraps=coalesce_ranges) as coalesce:
            self.assertEqual(
                summarize_ranges(values), {"value_count": 4, "range_count": 2}
            )
        coalesce.assert_called_once_with(values)

    def test_statistics_from_wide_coalesced_ranges(self):
        # Isolate aggregation from input collection: no interval expansion is
        # needed even when a dependency returns an enormous inclusive range.
        big = 10**100
        with patch("range_summary_stats.coalesce_ranges", return_value=[(-big, big)]):
            self.assertEqual(
                summarize_ranges(iter(())),
                {"value_count": 2 * big + 1, "range_count": 1},
            )

    def test_exhaustive_small_inputs(self):
        for length in range(5):
            for values in itertools.product(range(-2, 3), repeat=length):
                with self.subTest(values=values):
                    unique = set(values)
                    expected_ranges = sum(value - 1 not in unique for value in unique)
                    self.assertEqual(
                        summarize_ranges(values),
                        {"value_count": len(unique), "range_count": expected_ranges},
                    )


if __name__ == "__main__":
    unittest.main()
