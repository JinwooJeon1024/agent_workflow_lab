"""Reproduce a review of one immutable commit without changing tracked code."""

from __future__ import annotations

import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib
import itertools
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tarfile


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/evidence/difference-phase2"
REVIEWED = "fc1d8a1ce189b225a431286b98daaa35ec35e84c"
BASE = "5eb289c2a216dd98a25031b33adb4916c4c7c40a"
GIT = [
    r"C:\Program Files\Git\cmd\git.exe",
    "-c", "safe.directory=C:/Users/전진우/Documents/GitHub/agent_workflow_lab",
]
PYTHON = Path(r"C:\Users\전진우\AppData\Local\Programs\Python\Python312\python3.exe")


def oracle_checks(snapshot: Path) -> None:
    sys.path.insert(0, str(snapshot))
    module = importlib.import_module("range_summary")
    assert Path(module.__file__).resolve() == snapshot / "range_summary.py"
    difference = module.difference_ranges
    counts: Counter[str] = Counter()

    def oracle(left, right):
        remaining = sorted(set(left).difference(right))
        groups = itertools.groupby(enumerate(remaining), lambda item: item[1] - item[0])
        result = []
        for _, group in groups:
            values = [value for _, value in group]
            result.append((values[0], values[-1]))
        return result

    def check(left, right, category):
        left_before, right_before = left.copy(), right.copy()
        expected = oracle(left, right)
        actual = difference(left, right)
        assert actual == expected, f"{category} case {counts[category]} failed"
        assert left == left_before and right == right_before
        assert type(actual) is list
        assert all(type(pair) is tuple and len(pair) == 2 for pair in actual)
        assert all(type(v) is int for pair in actual for v in pair)
        assert all(a <= b for a, b in actual)
        assert all(actual[i][1] + 1 < actual[i + 1][0] for i in range(len(actual) - 1))
        counts[category] += 1

    directed = [
        ([], []), ([], [1]), ([1], []), ([1], [1]), ([1], [2]),
        (list(range(-4, 5)), [-4]), (list(range(-4, 5)), [4]),
        (list(range(-4, 5)), [-4, 4]), (list(range(-4, 5)), [0]),
        (list(range(-4, 5)), [-5, 5]),
        ([0, 2, 4, 6, 8], list(range(-1, 10))),
        ([0, 1, 4, 5, 8, 9], list(range(1, 9))),
        ([0, 1, 4, 5, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8]),
        (list(range(12)), [1, 3, 5, 7, 9, 11]),
        ([2, 1, 1, -2, -1, 5], [5, 5, -2]),
    ]
    for left, right in directed:
        check(left, right, "directed")

    domain = range(-4, 5)
    subsets = [list(s) for n in range(10) for s in itertools.combinations(domain, n)]
    for left in subsets:
        for right in subsets:
            check(left[::-1] + left, right + right[::-1], "exhaustive_subset_pairs")

    rng = random.Random(20261101)
    huge = 10**5000
    anchors = [-huge, -(10**100), 0, 10**100, huge]
    for index in range(12000):
        def generate():
            values = [rng.randrange(-80, 81) for _ in range(rng.randrange(71))]
            if index % 3 == 0:
                values += [rng.choice(anchors) + rng.randrange(-4, 5) for _ in range(12)]
            rng.shuffle(values)
            return values
        left, right = generate(), generate()
        check(left, right, "seeded_random_pairs")
        if index < 2000:
            shift = rng.choice(anchors)
            check([v + shift for v in left], [v + shift for v in right], "translated_pairs")
    check(list(range(-10000, 10001)), list(range(-10000, 10001, 2)), "dense_stress")
    check(list(range(-10000, 10001, 2)), list(range(-9999, 10000)), "dense_stress")

    events = []
    class Once:
        def __init__(self, name, values):
            self.name, self.values, self.calls = name, list(values), 0
        def __iter__(self):
            self.calls += 1
            assert self.calls == 1
            events.append((self.name, "iter"))
            for value in self.values:
                events.append((self.name, value))
                yield value
            events.append((self.name, "done"))
    left, right = Once("left", [3, 1, 2, 2, 7]), Once("right", [2, 7])
    assert difference(left, right) == [(1, 1), (3, 3)]
    assert events == [
        ("left", "iter"), ("left", 3), ("left", 1), ("left", 2),
        ("left", 2), ("left", 7), ("left", "done"),
        ("right", "iter"), ("right", 2), ("right", 7), ("right", "done"),
    ]
    assert (left.calls, right.calls) == (1, 1)
    counts["consumption_contracts"] += 1
    for name, values, expected in [
        ("shared_iterator", iter([3, 1, 2, 2, 7]), [(1, 3), (7, 7)]),
        ("shared_list", [3, 1, 2, 2, 7], []),
    ]:
        assert difference(values, values) == expected, name
        counts["consumption_contracts"] += 1

    class IntSubclass(int):
        pass
    for invalid in [True, False, 1.0, "1", None, IntSubclass(1), [], {}, (), object(), complex(1)]:
        for other in [[], [1], [999]]:
            for left, right in [([1, invalid, 2], other), (other, [1, invalid, 2])]:
                try:
                    difference(iter(left), iter(right))
                except TypeError:
                    pass
                else:
                    raise AssertionError("invalid element accepted")
                counts["invalid_elements"] += 1
    for invalid in [None, 7, True, 1.0, object()]:
        for left, right in [(invalid, []), ([], invalid)]:
            try:
                difference(left, right)
            except TypeError:
                pass
            else:
                raise AssertionError("non-iterable accepted")
            counts["invalid_arguments"] += 1

    class OriginalError(Exception):
        pass
    for side in ["left", "right"]:
        def failing():
            yield 1
            raise OriginalError(side)
        left, right = (failing(), []) if side == "left" else ([], failing())
        try:
            difference(left, right)
        except OriginalError as error:
            assert str(error) == side
        else:
            raise AssertionError("iterator exception hidden")
        counts["iteration_exceptions"] += 1

    original = module.coalesce_ranges
    calls = []
    def recording(values):
        calls.append(values)
        return original(values)
    left, right = [1, 2, 3], [2]
    try:
        module.coalesce_ranges = recording
        assert difference(left, right) == [(1, 1), (3, 3)]
        assert len(calls) == 2 and calls[0] is left and calls[1] is right
        counts["normalization_reuse"] += 1
    finally:
        module.coalesce_ranges = original

    # Isolate interval subtraction from normalization; inputs here are sentinels.
    # This checks huge normalized endpoints without enumerating their interiors.
    left_marker, right_marker = object(), object()
    def normalized(values):
        if values is left_marker:
            return [(-huge, -huge + 2), (0, 2), (huge, huge + 2)]
        assert values is right_marker
        return [(-huge + 1, huge + 1)]
    try:
        module.coalesce_ranges = normalized
        assert difference(left_marker, right_marker) == [(-huge, -huge), (huge + 2, huge + 2)]
        counts["huge_normalized_span"] += 1
    finally:
        module.coalesce_ranges = original

    print(json.dumps({"seed": 20261101, "counts": dict(counts), "total": sum(counts.values())}, indent=2))


def run_review() -> None:
    assert sys.version_info[:2] == (3, 12), sys.version
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    scratch = ROOT / "__pycache__/difference-review"
    scratch.mkdir(parents=True, exist_ok=True)
    snapshot = scratch / REVIEWED
    snapshot.mkdir(exist_ok=False)
    archive = scratch / f"{REVIEWED}.tar"
    commands = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")

    def execute(label, command, cwd=ROOT, expected=0):
        start = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(command, cwd=cwd, capture_output=True, env=environment)
        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        record = {
            "label": label, "argv": [str(arg) for arg in command], "cwd": str(cwd),
            "started_utc": start, "finished_utc": datetime.now(timezone.utc).isoformat(),
            "exit_code": result.returncode, "expected_exit_code": expected,
            "stdout": stdout, "stderr": stderr,
        }
        commands.append(record)
        (EVIDENCE / "independent-commands.json").write_text(
            json.dumps(commands, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
        log = f"COMMAND: {subprocess.list2cmdline([str(x) for x in command])}\nCWD: {cwd}\nEXIT: {result.returncode}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        (EVIDENCE / f"independent-{label}.log").write_text(log, encoding="utf-8")
        print(f"{label}: exit={result.returncode}", flush=True)
        assert result.returncode == expected, label
        return stdout

    execute("python-version", [PYTHON, "--version"])
    reviewed_sha = execute("reviewed-sha", GIT + ["rev-parse", REVIEWED]).strip()
    assert reviewed_sha == REVIEWED
    execute("ancestry", GIT + ["merge-base", "--is-ancestor", BASE, REVIEWED])
    execute("ignored-snapshot", GIT + ["check-ignore", "__pycache__/difference-review/snapshot"])
    execute("archive", GIT + ["archive", "--format=tar", "--output", archive, REVIEWED])
    with tarfile.open(archive) as source:
        members = source.getmembers()
        source.extractall(snapshot, filter="data")
    manifest = []
    for member in members:
        if member.isfile():
            data = (snapshot / member.name).read_bytes()
            manifest.append({"path": member.name, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)})
    manifest.sort(key=lambda item: item["path"])
    canonical = "".join(f"{item['sha256']}  {item['path']}\n" for item in manifest).encode()
    hashes = {
        "reviewed_sha": REVIEWED, "base_sha": BASE,
        "snapshot": str(snapshot), "archive": str(archive),
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256(canonical).hexdigest(),
        "manifest_hash_method": "SHA256 of sorted UTF-8 lines: '<file SHA256>  <relative path>\\n'",
        "files": manifest,
    }
    (EVIDENCE / "independent-snapshot.json").write_text(json.dumps(hashes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    changed = execute("changed-files", GIT + ["diff", "--name-status", BASE, REVIEWED])
    assert changed.splitlines() == ["M\trange_summary.py", "A\ttests/test_range_difference.py"]
    execute("diff-check", GIT + ["diff", "--check", BASE, REVIEWED])
    execute("reviewed-diff", GIT + ["diff", BASE, REVIEWED, "--", "range_summary.py", "tests/test_range_difference.py"])
    base_source = execute("base-source", GIT + ["show", f"{BASE}:range_summary.py"])
    old_ast = ast.parse(base_source)
    new_ast = ast.parse((snapshot / "range_summary.py").read_text(encoding="utf-8"))
    new_ast.body = [node for node in new_ast.body if not isinstance(node, ast.FunctionDef) or node.name != "difference_ranges"]
    assert ast.dump(old_ast, include_attributes=False) == ast.dump(new_ast, include_attributes=False)
    print("preservation: existing module AST identical after removing the new function", flush=True)
    execute("unit-tests", [PYTHON, "-m", "unittest", "discover", "-s", "tests", "-v"], snapshot)
    execute("doctest", [PYTHON, "-m", "doctest", "-v", "docs/spec.md"], snapshot)
    example = execute("cli-example", [PYTHON, "-m", "range_summary", "3", "1", "2", "2", "6"], snapshot)
    assert example == "[[1, 3], [6, 6]]\r\n" or example == "[[1, 3], [6, 6]]\n"
    empty = execute("cli-empty", [PYTHON, "-m", "range_summary"], snapshot)
    assert empty in ["[]\n", "[]\r\n"]
    execute("cli-invalid", [PYTHON, "-m", "range_summary", "not-an-integer"], snapshot, expected=2)
    execute("oracle", [PYTHON, Path(__file__).resolve(), "--oracle", snapshot], snapshot)
    for entry in manifest:
        assert hashlib.sha256((snapshot / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
    result = {"status": "passed", "tracked_snapshot_files_unchanged": len(manifest), "commands": len(commands)}
    (EVIDENCE / "independent-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--oracle":
        oracle_checks(Path(sys.argv[2]).resolve())
    else:
        run_review()
