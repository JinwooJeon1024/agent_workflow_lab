"""Acceptance tests for the compact range formatting API."""

import sys
import unittest

from range_summary import format_ranges


class FormatRangesTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(format_ranges([]), "")

    def test_single_and_gapped_values(self):
        self.assertEqual(format_ranges([9, 1, 5]), "1,5,9")

    def test_unsorted_duplicates_and_consecutive_values(self):
        self.assertEqual(format_ranges([3, 1, 2, 2, 6]), "1-3,6")

    def test_negative_ranges_and_zero(self):
        self.assertEqual(format_ranges([-1, -3, -2, 0, 4]), "-3-0,4")
        self.assertEqual(format_ranges([-3, -2, -1, 2]), "-3--1,2")

    def test_arbitrary_size_integers(self):
        big = 10**100
        self.assertEqual(format_ranges([big + 1, -big, big]),
                         f"{-big},{big}-{big + 1}")

    def test_one_shot_iterable(self):
        class OneShot:
            def __init__(self):
                self.iterations = 0

            def __iter__(self):
                self.iterations += 1
                if self.iterations > 1:
                    raise AssertionError("iterable consumed more than once")
                yield from [4, 2, 3]

        values = OneShot()
        self.assertEqual(format_ranges(values), "2-4")
        self.assertEqual(values.iterations, 1)

    def test_integers_beyond_decimal_conversion_limit(self):
        big = 10**5000
        digits = "1" + "0" * 5000
        next_digits = "1" + "0" * 4999 + "1"
        original_limit = sys.get_int_max_str_digits()
        self.assertEqual(format_ranges([-big, big, big + 1]),
                         f"-{digits},{digits}-{next_digits}")
        self.assertEqual(sys.get_int_max_str_digits(), original_limit)

    def test_input_not_mutated(self):
        values = [3, 1, 2, 2]
        self.assertEqual(format_ranges(values), "1-3")
        self.assertEqual(values, [3, 1, 2, 2])

    def test_invalid_elements(self):
        class IntegerSubclass(int):
            pass

        for invalid in (True, False, 1.0, "1", None, IntegerSubclass(1)):
            with self.subTest(invalid=repr(invalid)):
                with self.assertRaises(TypeError):
                    format_ranges(iter([1, invalid, 2]))


if __name__ == "__main__":
    unittest.main()
