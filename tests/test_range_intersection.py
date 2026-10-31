"""Acceptance tests for intersection of two integer iterables."""

import itertools
import unittest

from range_summary import intersect_ranges


class IntersectRangesTests(unittest.TestCase):
    def test_empty_inputs(self):
        for left, right in (([], []), ([], [1, 2]), ([1, 2], [])):
            with self.subTest(left=left, right=right):
                self.assertEqual(intersect_ranges(left, right), [])

    def test_disjoint_inputs(self):
        self.assertEqual(intersect_ranges([1, 2], [3, 4]), [])
        self.assertEqual(intersect_ranges([3, 4], [1, 2]), [])

    def test_single_common_value(self):
        self.assertEqual(intersect_ranges([7, 7], [7]), [(7, 7)])

    def test_unsorted_duplicates(self):
        self.assertEqual(
            intersect_ranges([6, 3, 2, 1, 2], [2, 3, 4, 6, 6]),
            [(2, 3), (6, 6)],
        )

    def test_negative_values_and_zero(self):
        self.assertEqual(
            intersect_ranges([-3, -2, -1, 0, 1, 4], [-2, -1, 0, 2, 4]),
            [(-2, 0), (4, 4)],
        )

    def test_contained_range(self):
        self.assertEqual(intersect_ranges(range(1, 6), [2, 3, 4]), [(2, 4)])
        self.assertEqual(intersect_ranges([2, 3, 4], range(1, 6)), [(2, 4)])

    def test_gaps_in_one_input_split_the_result(self):
        sparse = [-4, -2, 0, 2, 4]
        expected = [(value, value) for value in sparse]
        self.assertEqual(intersect_ranges(range(-4, 5), sparse), expected)
        self.assertEqual(intersect_ranges(sparse, range(-4, 5)), expected)

    def test_equal_range_ends(self):
        self.assertEqual(
            intersect_ranges([1, 2, 4, 5, 8], [0, 1, 2, 5, 6, 8, 9]),
            [(1, 2), (5, 5), (8, 8)],
        )

    def test_arbitrary_size_integers_and_large_gaps(self):
        big = 10**5000
        self.assertEqual(
            intersect_ranges(
                [-big, -big + 1, big, big + 1, big + 3],
                [-big + 1, big, big + 1, big + 2],
            ),
            [(-big + 1, -big + 1), (big, big + 1)],
        )

    def test_independent_one_shot_inputs_consumed_fully_once(self):
        class SinglePass:
            def __init__(self, values):
                self.values = values
                self.iterations = 0
                self.consumed = 0

            def __iter__(self):
                self.iterations += 1
                if self.iterations != 1:
                    raise AssertionError("input iterated more than once")
                for value in self.values:
                    self.consumed += 1
                    yield value

        left = SinglePass([1, 2, 3, 9])
        right = SinglePass([2, 3, 5, 7])
        self.assertEqual(intersect_ranges(left, right), [(2, 3)])
        self.assertEqual((left.iterations, right.iterations), (1, 1))
        self.assertEqual((left.consumed, right.consumed), (4, 4))

    def test_inputs_not_mutated(self):
        left = [3, 1, 2, 2, 6]
        right = [6, 2, 3, 4, 3]
        self.assertEqual(intersect_ranges(left, right), [(2, 3), (6, 6)])
        self.assertEqual(left, [3, 1, 2, 2, 6])
        self.assertEqual(right, [6, 2, 3, 4, 3])

    def test_mixed_iterable_types(self):
        self.assertEqual(intersect_ranges((1, 2, 3, 5), {2, 3, 4, 5}),
                         [(2, 3), (5, 5)])
        self.assertEqual(intersect_ranges(range(-2, 3), (v for v in [-1, 0, 4])),
                         [(-1, 0)])

    def test_invalid_elements_in_either_input_even_without_overlap(self):
        class IntegerSubclass(int):
            pass

        for invalid in (True, False, 1.0, "1", None, IntegerSubclass(1), [], {}):
            for other in ([], [9], [1]):
                for invalid_side in ("left", "right"):
                    with self.subTest(invalid=repr(invalid), other=other,
                                      invalid_side=invalid_side):
                        values = iter([1, invalid, 2])
                        left, right = (
                            (values, other) if invalid_side == "left" else (other, values)
                        )
                        with self.assertRaises(TypeError):
                            intersect_ranges(left, right)

    def test_non_iterable_arguments(self):
        for invalid in (None, 7, True):
            with self.subTest(invalid=invalid):
                with self.assertRaises(TypeError):
                    intersect_ranges(invalid, [])
                with self.assertRaises(TypeError):
                    intersect_ranges([], invalid)

    def test_same_reiterable_collection(self):
        values = [3, 1, 2, 2, 7]
        self.assertEqual(intersect_ranges(values, values), [(1, 3), (7, 7)])
        self.assertEqual(values, [3, 1, 2, 2, 7])

    def test_shared_iterator_is_consumed_sequentially(self):
        values = iter([3, 1, 2])
        self.assertEqual(intersect_ranges(values, values), [])
        self.assertEqual(list(values), [])

    def test_all_small_subsets_against_independent_oracle(self):
        domain = tuple(range(-2, 3))
        subsets = [
            subset
            for length in range(len(domain) + 1)
            for subset in itertools.combinations(domain, length)
        ]
        for left, right in itertools.product(subsets, repeat=2):
            with self.subTest(left=left, right=right):
                common = {value for value in domain if value in left and value in right}
                starts = [
                    value for value in domain
                    if value in common and value - 1 not in common
                ]
                ends = [
                    value for value in domain
                    if value in common and value + 1 not in common
                ]
                expected = list(zip(starts, ends))
                left_values = list(reversed(left)) + list(left[:1])
                right_values = list(right) + list(reversed(right))
                actual = intersect_ranges(left_values, right_values)
                self.assertEqual(actual, expected)
                self.assertEqual(intersect_ranges(right_values, left_values), actual)


if __name__ == "__main__":
    unittest.main()
