"""Acceptance tests, frozen before the deliberate defect is repaired."""

import itertools
import json
from pathlib import Path
import subprocess
import sys
import unittest

from range_summary import coalesce_ranges


ROOT = Path(__file__).resolve().parents[1]


class CoalesceRangesTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(coalesce_ranges([]), [])

    def test_single(self):
        self.assertEqual(coalesce_ranges([7]), [(7, 7)])

    def test_duplicates(self):
        self.assertEqual(coalesce_ranges([4, 4, 4]), [(4, 4)])

    def test_consecutive(self):
        self.assertEqual(coalesce_ranges([1, 2, 3]), [(1, 3)])

    def test_unsorted_and_duplicates(self):
        self.assertEqual(coalesce_ranges([3, 1, 2, 2, 6]), [(1, 3), (6, 6)])

    def test_negative_through_zero(self):
        self.assertEqual(coalesce_ranges([0, -2, -1, 4]), [(-2, 0), (4, 4)])

    def test_gaps(self):
        self.assertEqual(coalesce_ranges([9, 1, 5]), [(1, 1), (5, 5), (9, 9)])

    def test_arbitrary_size_integers(self):
        big = 10**100
        self.assertEqual(coalesce_ranges([big + 1, -big, big]),
                         [(-big, -big), (big, big + 1)])

    def test_one_shot_iterable(self):
        self.assertEqual(coalesce_ranges(iter([4, 2, 3])), [(2, 4)])

    def test_input_not_mutated(self):
        values = [3, 1, 2, 2]
        before = values.copy()
        coalesce_ranges(values)
        self.assertEqual(values, before)

    def test_invalid_elements(self):
        class IntegerSubclass(int):
            pass

        for invalid in (True, False, 1.0, "1", None, [], {}, IntegerSubclass(1)):
            with self.subTest(invalid=repr(invalid)):
                with self.assertRaises(TypeError):
                    coalesce_ranges([1, invalid, 2])

    def test_exhaustive_small_domain(self):
        # 1 + 5 + 25 + 125 + 625 = 781 inputs. Check the contract's invariants
        # independently of the grouping implementation.
        for length in range(5):
            for values in itertools.product(range(-2, 3), repeat=length):
                with self.subTest(values=values):
                    ranges = coalesce_ranges(values)
                    self.assertEqual(
                        [v for start, end in ranges for v in range(start, end + 1)],
                        sorted(set(values)),
                    )
                    self.assertTrue(all(start <= end for start, end in ranges))
                    self.assertTrue(all(
                        left[1] + 1 < right[0]
                        for left, right in zip(ranges, ranges[1:])
                    ))


class CLITests(unittest.TestCase):
    def run_cli(self, *values):
        return subprocess.run(
            [sys.executable, "-m", "range_summary", *values],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=False,
        )

    def test_cli_example(self):
        result = self.run_cli("3", "1", "2", "2", "6")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "[[1, 3], [6, 6]]\n")
        self.assertEqual(result.stderr, "")

    def test_cli_empty(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [])

    def test_cli_negatives(self):
        result = self.run_cli("0", "-2", "-1", "4")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [[-2, 0], [4, 4]])

    def test_cli_invalid_integer(self):
        result = self.run_cli("1", "not-an-integer")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid int value", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
