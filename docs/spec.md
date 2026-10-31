# Spec: coalesce integer ranges

## Goal

Implement `range_summary.coalesce_ranges(values)` using Python 3.12 and the
standard library. It accepts a finite iterable of built-in integers and returns
sorted, maximal, inclusive `(start, end)` tuples covering exactly the distinct
input values. Adjacent integers belong to one range; gaps remain separate.

Examples:

- `[] -> []`
- `[3, 1, 2, 2, 6] -> [(1, 3), (6, 6)]`
- `[0, -2, -1, 4] -> [(-2, 0), (4, 4)]`

Consume an iterable once without mutating the caller's input. Reject booleans,
floats, strings, and every other non-built-in-integer element with `TypeError`.
Support arbitrary-size integers. Expected complexity: O(n log n) time, O(n) space.

The CLI `python3 -m range_summary [INTEGER ...]` prints the same ranges as a JSON
array of two-element arrays, with a trailing newline. No arguments prints `[]`.
Malformed CLI integers produce argparse's nonzero exit status (2).

## Executable acceptance criteria

1. `python3 -m unittest discover -s tests -v` runs at least one test and exits 0.
   Cover empty/single/duplicate/unsorted/negative/gapped/consecutive input,
   arbitrary-size integers, one-shot iterables, input preservation, invalid types,
   an exhaustive small input domain, and successful/invalid CLI requests.
2. `python3 -m range_summary 3 1 2 2 6` exits 0 and prints `[[1, 3], [6, 6]]`.
3. On `pull_request` events, GitHub Actions executes that same test suite on
   GitHub's standard `ubuntu-latest` runner with Python 3.12, a read-only
   `GITHUB_TOKEN`, no secrets, and no third-party Python dependencies.
4. Record one deliberately flawed implementation, its real failing test output,
   and a Codex repair with unchanged tests. Allow no more than three repair
   attempts; stop and report if the budget is exhausted. Do not skip tests,
   weaken assertions, or mark the defect as an expected failure.
5. Review the final code and CI in a separate Codex context that did not implement
   the change; record the reviewed commit, executed checks, and findings.
6. Create a Draft PR to `main`; retain the actual PR URL, Actions run URL,
   commit SHA, event, conclusion, and job/step results. Until a real run succeeds,
   this experiment is incomplete even if every local test passes.

## Boundaries and measurement

Use existing Codex and GitHub Actions; do not build a new orchestrator. This run
is one Codex-directed experiment, not proof of unattended handling of arbitrary
future specs or automatic Codex execution inside GitHub Actions.

Count repair attempts separately from normal checks. Count human interventions
as additional human instructions, approvals, configuration actions, or manual
repairs after the execution request; the request itself is the initial input.
Report invisible configuration actions as unknown rather than assuming zero.
Do not change repository permissions/settings, purchase services, merge, deploy,
or enter credentials. Those operations need human approval. Git pushes and a
Draft PR for this experiment are part of the requested work.
