"""Acceptance tests for directional difference of two integer iterables."""

import itertools
import unittest

from range_summary import difference_ranges


class DifferenceRangesTests(unittest.TestCase):
    def test_empty_inputs(self):
        self.assertEqual(difference_ranges([], []), [])
        self.assertEqual(difference_ranges([], [1, 2]), [])
        self.assertEqual(difference_ranges([3, 1, 2, 2, 6], []), [(1, 3), (6, 6)])

    def test_disjoint_and_adjacent_inputs(self):
        for right in ([8, 9], [-2, -1], [0, 4], [-2, 0, 4, 8]):
            with self.subTest(right=right):
                self.assertEqual(difference_ranges([1, 2, 3], right), [(1, 3)])

    def test_direction_matters(self):
        self.assertEqual(difference_ranges([1, 2, 3], [2, 3, 4]), [(1, 1)])
        self.assertEqual(difference_ranges([2, 3, 4], [1, 2, 3]), [(4, 4)])

    def test_identical_values_are_removed(self):
        self.assertEqual(difference_ranges([3, 1, 2, 2], [2, 3, 1, 1]), [])

    def test_unsorted_duplicates(self):
        self.assertEqual(
            difference_ranges([6, 3, 2, 1, 2], [2, 8, 2]),
            [(1, 1), (3, 3), (6, 6)],
        )

    def test_negative_values_and_zero(self):
        self.assertEqual(
            difference_ranges([-3, -2, -1, 0, 2], [-2, 2]),
            [(-3, -3), (-1, 0)],
        )

    def test_single_hole_splits_left_range(self):
        self.assertEqual(difference_ranges(range(5), [2]), [(0, 1), (3, 4)])

    def test_both_endpoints_removed(self):
        self.assertEqual(difference_ranges(range(5), [0, 4]), [(1, 3)])

    def test_many_right_ranges_split_one_left_range(self):
        self.assertEqual(
            difference_ranges(range(-5, 8), [-4, -3, 0, 3, 4, 7]),
            [(-5, -5), (-2, -1), (1, 2), (5, 6)],
        )

    def test_one_right_range_spans_multiple_left_ranges(self):
        self.assertEqual(difference_ranges([1, 3, 5], range(7)), [])
        self.assertEqual(
            difference_ranges([0, 1, 3, 4, 6, 7, 9, 10], range(1, 10)),
            [(0, 0), (10, 10)],
        )

    def test_equal_endpoints_then_later_overlap(self):
        self.assertEqual(
            difference_ranges([1, 2, 4, 5, 8, 9], [0, 1, 2, 5, 6, 8]),
            [(4, 4), (9, 9)],
        )

    def test_arbitrary_size_integers_and_large_gaps(self):
        big = 10**5000
        self.assertEqual(
            difference_ranges(
                [-big, -big + 1, 0, big, big + 1], [-big + 1, big],
            ),
            [(-big, -big), (0, 0), (big + 1, big + 1)],
        )

    def test_inputs_not_mutated(self):
        left, right = [3, 1, 2, 2, 6], [2, 8]
        self.assertEqual(difference_ranges(left, right), [(1, 1), (3, 3), (6, 6)])
        self.assertEqual(left, [3, 1, 2, 2, 6])
        self.assertEqual(right, [2, 8])

    def test_mixed_iterable_types(self):
        self.assertEqual(difference_ranges((1, 2, 3, 5), {2, 3, 4}), [(1, 1), (5, 5)])
        self.assertEqual(
            difference_ranges(range(-2, 3), (v for v in [-1, 0, 4])),
            [(-2, -2), (1, 2)],
        )

    def test_independent_one_shot_inputs_consumed_once_left_then_right(self):
        events = []

        class Once:
            def __init__(self, name, values):
                self.name = name
                self.values = iter(values)
                self.calls = 0

            def __iter__(self):
                self.calls += 1
                if self.calls != 1:
                    raise AssertionError("input consumed twice")
                events.append(self.name)
                return self.values

        left = Once("left", [3, 1, 2, 6])
        right = Once("right", [2, 8])
        self.assertEqual(difference_ranges(left, right), [(1, 1), (3, 3), (6, 6)])
        self.assertEqual(events, ["left", "right"])
        self.assertEqual((left.calls, right.calls), (1, 1))
        self.assertEqual(list(left.values), [])
        self.assertEqual(list(right.values), [])

    def test_same_reiterable_collection(self):
        values = [3, 1, 2, 2, 7]
        self.assertEqual(difference_ranges(values, values), [])
        self.assertEqual(values, [3, 1, 2, 2, 7])

    def test_shared_iterator_is_consumed_sequentially(self):
        values = iter([3, 1, 2, 2, 7])
        self.assertEqual(difference_ranges(values, values), [(1, 3), (7, 7)])
        self.assertEqual(list(values), [])

    def test_invalid_elements_in_either_input_even_if_empty_or_removed(self):
        class IntegerSubclass(int):
            pass

        for invalid in (True, False, 1.0, "1", None, IntegerSubclass(1), [], {}):
            for other in ([], [9], [1]):
                for side in ("left", "right"):
                    with self.subTest(invalid=repr(invalid), other=other, side=side):
                        values = iter([1, invalid, 2])
                        left, right = (values, other) if side == "left" else (other, values)
                        with self.assertRaises(TypeError):
                            difference_ranges(left, right)

    def test_non_iterable_arguments(self):
        for invalid in (None, 7, True):
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    difference_ranges(invalid, [])
                with self.assertRaises(TypeError):
                    difference_ranges([], invalid)

    def test_all_small_subsets_against_independent_oracle(self):
        domain = tuple(range(-3, 4))
        subsets = [
            subset for size in range(len(domain) + 1)
            for subset in itertools.combinations(domain, size)
        ]
        for left, right in itertools.product(subsets, repeat=2):
            with self.subTest(left=left, right=right):
                remaining = set(left) - set(right)
                starts = [v for v in domain if v in remaining and v - 1 not in remaining]
                ends = [v for v in domain if v in remaining and v + 1 not in remaining]
                expected = list(zip(starts, ends))
                actual = difference_ranges(
                    list(reversed(left)) + list(left),
                    list(right) + list(reversed(right)),
                )
                self.assertEqual(actual, expected)
                self.assertIs(type(actual), list)
                for interval in actual:
                    self.assertIs(type(interval), tuple)
                    self.assertTrue(all(type(v) is int for v in interval))


if __name__ == "__main__":
    unittest.main()
