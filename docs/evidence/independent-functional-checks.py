"""Independent checks: executed outside the reviewed source tree."""
from itertools import combinations
from pathlib import Path
import json
import random
import subprocess
import sys

SNAPSHOT = Path('/tmp/agent-workflow-independent-review')
sys.path.insert(0, str(SNAPSHOT))
from range_summary import coalesce_ranges

assert Path(sys.modules['range_summary'].__file__).parent == SNAPSHOT

def oracle(values):
    present = set(values)
    starts = sorted(value for value in present if value - 1 not in present)
    ends = sorted(value for value in present if value + 1 not in present)
    return list(zip(starts, ends))

def check_api(values):
    before = values.copy()
    actual = coalesce_ranges(values)
    assert type(actual) is list
    assert all(type(pair) is tuple and len(pair) == 2 for pair in actual)
    assert all(type(bound) is int for pair in actual for bound in pair)
    assert actual == oracle(before), (values, actual, oracle(before))
    assert values == before

api_count = 0
for size in range(12):
    for subset in combinations(range(-5, 6), size):
        check_api(list(reversed(subset)))
        api_count += 1
print('Exhaustive distinct subsets over -5..5: 2048 passed')

rng = random.Random(20261031)
for _ in range(1000):
    values = [rng.randrange(-100, 101) for _ in range(rng.randrange(101))]
    rng.shuffle(values)
    check_api(values)
    api_count += 1
print('Deterministic randomized sequences, duplicates, gaps and negatives: 1000 passed')

big = 10**10000
check_api([big + 2, -big + 1, big, -big, big + 1])
api_count += 1
print('API with 10001-digit positive and negative integers: passed')

class ExactlyOnce:
    def __init__(self):
        self.iterations = 0
    def __iter__(self):
        self.iterations += 1
        if self.iterations != 1:
            raise AssertionError('Iterable was traversed more than once')
        yield from (8, 6, 7, 7, 20)

once = ExactlyOnce()
assert coalesce_ranges(once) == [(6, 8), (20, 20)]
assert once.iterations == 1
api_count += 1
print('Custom iterable allowing exactly one traversal: passed')

class IntegerSubclass(int):
    pass
invalids = (True, False, 1.0, '1', None, [], {}, IntegerSubclass(3), complex(1), b'1', object())
for invalid in invalids:
    try:
        coalesce_ranges(iter([0, invalid, 1]))
    except TypeError:
        pass
    else:
        raise AssertionError('Non-built-in integer accepted')
print('Invalid API element types: 11 passed')

cli_cases = [
    ([], 0, '[]\n'),
    (['3', '1', '2', '2', '6'], 0, '[[1, 3], [6, 6]]\n'),
    (['-10', '-8', '-9', '0', '0', '+2'], 0, '[[-10, -8], [0, 0], [2, 2]]\n'),
    (['--', '-1', '0', '1'], 0, '[[-1, 1]]\n'),
    (['1.5'], 2, ''),
    (['1', 'not-an-integer'], 2, ''),
    ([str(10**100), str(10**100 + 1)], 0, json.dumps([[10**100, 10**100 + 1]]) + '\n'),
]
for args, expected_status, expected_stdout in cli_cases:
    command = [sys.executable, '-m', 'range_summary', *args]
    result = subprocess.run(command, cwd=SNAPSHOT, capture_output=True, text=True, timeout=10)
    print('COMMAND:', json.dumps(command))
    print('EXIT STATUS:', result.returncode)
    print('STDOUT:', repr(result.stdout))
    print('STDERR:', repr(result.stderr))
    assert result.returncode == expected_status
    assert result.stdout == expected_stdout
    if expected_status == 0:
        assert result.stderr == ''
    else:
        assert 'invalid int value' in result.stderr
        assert 'Traceback' not in result.stderr
print(f'INDEPENDENT RESULTS: {api_count} valid API cases + {len(invalids)} invalid-type cases + {len(cli_cases)} CLI subprocess cases passed')
