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

## Integer-set intersection API

`range_summary.intersect_ranges(left, right)` accepts two finite iterables of
built-in integers and returns their common distinct values as a sorted list of
maximal, inclusive `(start, end)` tuples. Inputs contain integers, not interval
pairs. For example, `[6, 3, 2, 1, 2]` and `[2, 3, 4, 6, 6]` return
`[(2, 3), (6, 6)]`; empty or disjoint sets return `[]`.

Acceptance criteria:

1. Support duplicates, arbitrary ordering, negative values, zero, and
   arbitrary-size integers without expanding intervals or gaps.
2. Consume each input once, left then right, without mutating caller collections.
   Independent one-shot inputs are supported. If arguments share an iterator's
   consumption state, no separate snapshot is made: passing the same iterator
   twice leaves the second input empty. A shared list remains re-iterable.
3. Reject every non-built-in-int element with `TypeError`, including booleans
   and int subclasses, even when the other input is empty or disjoint.
   After an invalid element raises, remaining input need not be consumed.
4. Reuse `coalesce_ranges` for both inputs before intersecting normalized ranges.
   Expected time is O(n log n + m log m), space O(n+m).
5. Preserve existing APIs, CLI JSON output, tests, and CI. The existing unittest
   discovery must pass, including boundary cases and an independent small-domain
   oracle for the new API. No new dependencies are required.

## Difference API — Phase 1 체크포인트 (계획된 중단)

- 상태: **Phase 1 완료 후 중단, Phase 2 미시작**. 실제 프로세스 충돌이나 장애 복구 실험이 아니다.
- 기준: `7fe9e7b7271478f9f0fbbd70486bc56e4c664cbb` (시작 시 fetch한 `origin/main`).
- 브랜치: `codex/difference-ranges-checkpoint`. 기존 작업 브랜치와 변경은 보존했다.
- Phase 1은 이 Spec만 변경한다. 기능·테스트 파일 구현, 독립 리뷰, Draft PR·CI 확인은 Phase 2다.
- 기준 검증: Python 3.12.1, `python3 -m unittest discover -s tests -v` **57개 통과**.
  아래 신규 doctest는 Phase 2 완료 조건이며 Phase 1에서 실행하거나 통과했다고 주장하지 않는다.
- **명시적인 Phase 2 재개 요청 전에는 구현을 시작하지 않는다.** 체크포인트 SHA는
  `git log -1 --format=%H -- docs/spec.md`로 확인한다(자기 SHA를 문서 안에 중복 저장하지 않는다).

### 계약과 기존 코드 분석

`range_summary.difference_ranges(left: Iterable[int], right: Iterable[int]) -> list[tuple[int, int]]`
는 두 유한 정수 iterable에서 `set(left) - set(right)`에 해당하는 값을 정렬된 최대 연속
포함 구간으로 반환한다. 입력은 구간 쌍이 아닌 정수 원소이며, 연산 방향은 왼쪽에서 오른쪽을 뺀다.

기존 `coalesce_ranges`가 built-in int만 허용하는 검증·단회 소비·정렬·중복 제거를 담당한다.
기존 `intersect_ranges`처럼 왼쪽, 오른쪽을 각각 정규화한 뒤 구간 두 포인터와 왼쪽 잔여 시작점을
사용해 차집합을 계산한다. 한 오른쪽 구간이 여러 왼쪽 구간에 걸칠 수 있으므로 포인터를 너무
일찍 버리지 않는다. 값 사이의 정수를 확장하지 않는다. 시간 O(n log n + m log m), 공간 O(n+m).

- 컬렉션을 변경하지 않고 각 입력을 한 번 소비한다. 음수·0·중복·임의 순서·임의 크기 정수를 지원한다.
- bool, int 하위 클래스 등 built-in int 이외 원소와 비-iterable 인자는 TypeError다.
  한쪽이 비거나 결과에서 사라지는 잘못된 원소도 거부한다. 오류 이후의 남은 소비는 보장하지 않는다.
- 기존 교집합과 같이 공유 iterator 상태를 복제하지 않는다. 같은 iterator 두 번은 오른쪽이
  이미 소진되어 왼쪽 정규화 결과를 반환한다. 같은 list 두 번은 빈 차집합이다.
- 기존 API·CLI·테스트·CI·의존성은 유지한다. 새 API에 CLI 옵션을 추가하지 않는다.

### 실행 가능한 Acceptance Criteria (Phase 2에서 실행)

완료 판정 명령: `python3 -m doctest -v docs/spec.md`. 아직 API가 없으므로 Phase 1에서는
미실행 상태다. Phase 2에서는 이 기준을 만족하는 `tests/test_range_difference.py`도 작성해
기존 unittest discovery와 PR CI에서 자동 실행되게 한다. 아래 블록은 큰 정수를 출력하지 않는다.

```pycon
>>> from range_summary import difference_ranges
>>> cases = (
...     ([], [], []),
...     ([], [1], []),
...     ([3, 1, 2, 2, 6], [], [(1, 3), (6, 6)]),
...     ([1, 2], [8], [(1, 2)]),
...     ([1, 2, 3], [1, 2, 3], []),
...     ([0, 1, 2, 3, 4], [2], [(0, 1), (3, 4)]),
...     ([0, 1, 2, 3, 4], [0, 4], [(1, 3)]),
...     ([-3, -2, -1, 0, 2], [-2, 2], [(-3, -3), (-1, 0)]),
...     ([1, 3, 5], [0, 1, 2, 3, 4, 5, 6], []),
... )
>>> assert all(difference_ranges(a, b) == expected for a, b, expected in cases)
>>> a, b = [3, 1, 2, 2, 6], [2, 8]
>>> before = (a.copy(), b.copy())
>>> assert difference_ranges(a, b) == [(1, 1), (3, 3), (6, 6)]
>>> assert difference_ranges(a, a) == [] and (a, b) == before
>>> class Once:
...     def __init__(self, values):
...         self.values = iter(values)
...         self.calls = 0
...     def __iter__(self):
...         self.calls += 1
...         assert self.calls == 1, "input consumed twice"
...         return self.values
>>> a, b = Once([3, 1, 2, 6]), Once([2, 8])
>>> assert difference_ranges(a, b) == [(1, 1), (3, 3), (6, 6)]
>>> assert (a.calls, b.calls) == (1, 1) and list(a.values) == list(b.values) == []
>>> shared = iter([3, 1, 2])
>>> assert difference_ranges(shared, shared) == [(1, 3)]
>>> big = 10**5000
>>> assert difference_ranges([-big, -big + 1, big, big + 1], [-big + 1, big]) == [(-big, -big), (big + 1, big + 1)]
>>> class IntegerSubclass(int):
...     pass
>>> for invalid in (True, False, 1.0, "1", None, IntegerSubclass(1), [], {}):
...     for other in ([], [9], [1]):
...         for a, b in (([1, invalid, 2], other), (other, [1, invalid, 2])):
...             try:
...                 difference_ranges(a, b)
...             except TypeError:
...                 pass
...             else:
...                 raise AssertionError("invalid element accepted")
>>> for a, b in ((None, []), ([], None), (7, []), ([], 7)):
...     try:
...         difference_ranges(a, b)
...     except TypeError:
...         pass
...     else:
...         raise AssertionError("non-iterable argument accepted")
>>> from itertools import combinations, product
>>> domain = tuple(range(-2, 3))
>>> subsets = [s for size in range(6) for s in combinations(domain, size)]
>>> def oracle(a, b):
...     remaining = {v for v in domain if v in a and v not in b}
...     starts = [v for v in domain if v in remaining and v - 1 not in remaining]
...     ends = [v for v in domain if v in remaining and v + 1 not in remaining]
...     return list(zip(starts, ends))
>>> assert all(difference_ranges(list(reversed(a)) + list(a), list(reversed(b)) + list(b)) == oracle(a, b) for a, b in product(subsets, repeat=2))

```

### Phase 2 재개 절차 (다음 세션은 이 절과 Git 상태만으로 재개)

1. 사람의 명시적 재개 요청 후 `git status --short --branch`로 변경을 확인·보존하고
   `git switch codex/difference-ranges-checkpoint`한다. 다른 clone이면 먼저 fetch해 같은 원격 브랜치를 추적한다.
   `AGENTS.md`와 이 절을 읽는다. 기준 SHA를 임의로 바꾸거나 기존 브랜치를 덮어쓰지 않는다.
2. 먼저 기존 unittest 57개가 통과하는지 확인한다. `range_summary.py`에 API를 구현하고
   `tests/test_range_difference.py`에 위 계약·경계·독립 oracle 테스트를 추가한다.
3. doctest, `python3 -m unittest discover -s tests -v`, 기존 CLI 예제, `git diff --check`를 실행한다.
   테스트를 약화하지 않고 실패 후 코드 수정은 최대 3회(현재 사용 0회)로 제한한다.
4. 정확한 구현 커밋을 구현에 참여하지 않은 별도 문맥에서 독립 리뷰하고 지적을 반영한다.
5. 브랜치를 push하고 한국어 Draft PR을 `main` 대상으로 생성한다. 기존 `pull_request` CI의
   head SHA·run URL·event·job/step·실제 테스트 로그와 성공 결론을 확인한다. 로컬 성공과 구분한다.
6. PR에 체크포인트→재개 커밋, 추가 사람 지시 수, 계획된 중단/재개였음을 기록한다.
   Phase 2는 변경 시점부터 별도 집계하며 PR 병합·권한/환경 변경·배포는 수행하지 않는다.
