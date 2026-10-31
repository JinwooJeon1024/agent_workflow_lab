# Execution report

## Status

**The controlled experiment has a real Draft PR and a successful GitHub Actions
run, in addition to the local failure/repair and independent review.**

- [Draft PR #1](https://github.com/JinwooJeon1024/agent_workflow_lab/pull/1), open and draft.
- [Verified pull_request CI run](https://github.com/JinwooJeon1024/agent_workflow_lab/actions/runs/41200564988), **success**.
- Tested PR head: `27d763df1ab201d640d947a487e79ab0adb7dedd`.
- Standard GitHub-hosted `ubuntu-latest` runner; actual image Ubuntu 26.04.1.
- All 16 unittest methods executed and passed; CLI smoke step also passed.

This report update adds evidence/documentation only. Its push triggers another
`synchronize` run. The final PR head, its matching final run, and post-CI
independent verification are recorded in the PR description after that run
finishes. The historical successful run above remains immutable evidence;
it is not silently represented as a run of a later commit.

## Scope and command evidence

All project commands run in `/workspace/agent_workflow_lab` unless another working
directory is stated. Python is 3.12.14; Git is 2.52.0; GitHub CLI is 2.46.0.
There is no dependency installation, long-lived service, or custom orchestrator.

| Stage | Commands actually executed | Observed result |
| --- | --- | --- |
| Preflight | `git status --short --branch`; `git ls-remote origin` | Empty, unborn checkout; successful Git transport, no remote refs. |
| GitHub API preflight | `gh api repos/JinwooJeon1024/agent_workflow_lab --jq '{full_name,visibility,default_branch,permissions,allow_forking,archived}'` | Exit 1; proxy returns `Forbidden`. An unauthenticated Python urllib request separately reports `Tunnel connection failed: 403 Forbidden`. |
| Establish PR base | `git branch -m main`; `git add .gitignore README.md`; `git -c user.name='Codex Experiment' -c user.email='codex@users.noreply.github.com' commit -m "chore: initialize public workflow experiment"`; `git push -u origin main` | All exit 0; remote `main` created at `9f976bef6bd113824e2590778efdf45c5d3078b5`. This is initial repository setup, not a PR merge. |
| Spec and implementation | `git switch -c codex/minimal-dev-loop`; files authored with shell here-documents; `git add README.md docs/spec.md .github/workflows/ci.yml range_summary.py tests/test_range_summary.py`; `git -c user.name='Codex Experiment' -c user.email='codex@users.noreply.github.com' commit -m "feat: specify range summary with tests and seeded adjacency defect"` | Spec, acceptance tests, workflow, CLI, and deliberately flawed implementation committed as `b06f68f149dd744b6b2ea04918cf62054c4e2b8e`. |
| Verify official action versions | `git ls-remote https://github.com/actions/checkout.git refs/tags/v4.2.2`; `git ls-remote https://github.com/actions/setup-python.git refs/tags/v5.6.0` | Both exit 0; remote tag SHAs match the full SHAs pinned in CI. |
| Freeze tests | `sha256sum tests/test_range_summary.py > /tmp/agent-workflow-evidence/tests-before.sha256` | Test SHA-256: `ad2800a8ae58de33bce43dc4c04593586e186ea561e6f154f75527c8c3e0794c`. |
| Deliberate failure | `set -o pipefail; python3 -m unittest discover -s tests -v 2>&1 \| tee /tmp/agent-workflow-evidence/red.log` | Underlying Python exit 1, preserved using `PIPESTATUS[0]`; 16 tests ran; 593 failure records, including subtests. No skipped tests or expected-failure treatment. |
| Codex repair attempt 1 of 3 | `apply_patch`: change only `if value == end:` to `if value == end + 1:` in `range_summary.py` | The de-duplicated sorted list needs adjacency comparison. The old comparison never merged distinct adjacent values. Tests and assertions untouched. |
| Re-test | `set -o pipefail; python3 -m unittest discover -s tests -v 2>&1 \| tee /tmp/agent-workflow-evidence/green.log` | Underlying Python exit 0; all 16 tests pass, including 781 exhaustive inputs in one test and four CLI subprocess tests. |
| Guard against test weakening | `sha256sum -c /tmp/agent-workflow-evidence/tests-before.sha256`; `git diff b06f68f HEAD -- tests/test_range_summary.py` | Exit 0, checksum OK; empty test diff. |
| Functional smoke | `python3 -m range_summary 3 1 2 2 6`; `actual="$(python3 -m range_summary 3 1 2 2 6)"`; `test "$actual" = '[[1, 3], [6, 6]]'` | Exit 0; exact expected JSON verified, not merely a running process. |
| Commit repair | `git diff --check`; `git add range_summary.py`; `git -c user.name='Codex Experiment' -c user.email='codex@users.noreply.github.com' commit -m "fix: merge adjacent integer values without weakening tests"` | Exit 0; `a1a32811713f789a8a6907a447a9d3d602e1b4af`, one-line implementation change. |
| Local workflow inspection | Python with `yaml.BaseLoader` parsed the YAML and asserted `pull_request`, `contents: read`, `ubuntu-latest`, a five-minute timeout, and the same unittest command | Exit 0. Local static inspection only; not a GitHub Actions result. PyYAML was already available and is not an application or CI dependency. |

The feature branch was pushed with `git push -u origin codex/minimal-dev-loop`
(exit 0), including the pinned GitHub Actions workflow.

The initial red run is not a repair retry. **Repair attempts used: 1/3.** No
unchanged failed command was repeatedly run to manufacture success. Later
independent validation is not a code-repair retry. No CI reruns have been used.

## Durable local evidence

- [Spec and acceptance criteria](spec.md)
- [Raw failing unittest output, gzip-compressed](evidence/red-unittest.log.gz)
- [Readable failing-output excerpt](evidence/red-excerpt.txt) (explicitly abbreviated)
- [Complete passing unittest output](evidence/green-unittest.log)
- [Machine-readable manifest with commit IDs, exit statuses, counts, and hashes](evidence/manifest.json)

Verify the raw red log by decompressing it and comparing SHA-256 with the
manifest. The original defect remains in Git history for reproduction. It is
not present in the final implementation. The complete red log contains 593
failure records because unittest counts each failing exhaustive subtest.
This is **16 test methods**, not 593 distinct test methods.

## Independent review

**Completed: no blocking findings.** A separate Codex context with no inherited
implementation conversation reviewed immutable commit
`a1a32811713f789a8a6907a447a9d3d602e1b4af` in an extracted Git archive outside the
working checkout. It independently ran all 16 tests (exit 0), 3,050 valid API cases,
11 invalid-type cases, and seven CLI subprocess cases. No code or tests were
changed. Its report explicitly distinguishes local/static review from remote CI.

[Full independent review and exact commands](evidence/independent-review.md).
The final changes after the reviewed commit contain evidence and documentation
only; the implementation, tests, and workflow are identical to the reviewed SHA.

## External evidence: initial blocker and successful resumption

The first API request and Draft PR creation were genuinely blocked at the cloud
proxy with HTTP 403. [Original creation error](evidence/pr-create.log) preserves
that failed attempt. Git transport was working. A minimal API-domain draft was
saved at that time; saving did not apply it. The user subsequently reported
publishing the environment. This task resumed in a new environment, whose
observed network policy was `unrestricted` and enforced. The agent did not
reapply old configuration or publish another environment version.

Existing injected authentication was reused; no new credentials were requested,
printed, copied, or stored in the repository. GitHub's API confirmed a public,
non-archived repository with default branch `main`. No repository settings,
token permissions, branch protection, or runner configuration were changed.

| Resumed stage | Actual command | Actual result |
| --- | --- | --- |
| API recheck | `gh api repos/JinwooJeon1024/agent_workflow_lab --jq '{full_name,visibility,default_branch,permissions,archived}'` | Exit 0; public, non-archived, default branch main. |
| Duplicate guard | `gh pr list --repo JinwooJeon1024/agent_workflow_lab --head codex/minimal-dev-loop --base main --state all --json number,url,state,isDraft,headRefOid` | Exit 0, `[]`; no existing PR. |
| Restored-instance validation | `python3 -m unittest discover -s tests -v`; `git diff --exit-code a1a32811713f789a8a6907a447a9d3d602e1b4af HEAD -- range_summary.py tests .github/workflows/ci.yml` | Both exit 0; 16 tests pass; source, tests, and workflow match independent review. [Log](evidence/restored-green.log). |
| Actual Draft PR creation | `gh pr create --repo JinwooJeon1024/agent_workflow_lab --base main --head codex/minimal-dev-loop --draft --title "Validate a minimal Codex development loop with Python tests" --body-file /tmp/agent-workflow-evidence/resumed-pr-body.md` | Exit 0; [PR #1](https://github.com/JinwooJeon1024/agent_workflow_lab/pull/1). [Creation output](evidence/pr-created.log). |
| PR state and checks | `gh pr view 1 --repo JinwooJeon1024/agent_workflow_lab --json number,url,state,isDraft,headRefOid,baseRefName,statusCheckRollup` | Exit 0; open, draft, base main; actual check present. |
| Automatic trigger inspection | `gh run list --repo JinwooJeon1024/agent_workflow_lab --branch codex/minimal-dev-loop --event pull_request --limit 5 --json databaseId,url,status,conclusion,event,headSha,workflowName,createdAt` | Exit 0; run 41200564988 automatically started for PR head 27d763d. No manual dispatch. |
| CI outcome and steps | `gh run view 41200564988 --repo JinwooJeon1024/agent_workflow_lab --json databaseId,url,status,conclusion,event,headSha,jobs,createdAt,updatedAt` | Exit 0; completed/success, pull_request, exact head SHA, all job/step conclusions success. [JSON](evidence/ci-opened.json). |
| Real test output | `gh run view 41200564988 --repo JinwooJeon1024/agent_workflow_lab --log` | Exit 0; `Ran 16 tests`, `OK`; CLI assertion step success. [Complete log](evidence/ci-opened.log). |
| Actual runner | `gh api repos/JinwooJeon1024/agent_workflow_lab/actions/jobs/124535369827 --jq '{id,status,conclusion,runner_name,runner_group_name,labels,head_sha,html_url}'` | Exit 0; runner group GitHub Actions; label ubuntu-latest; success. [JSON](evidence/ci-opened-runner.json). |

Both the unittest and documented CLI steps completed successfully on the real
runner. CI used Python 3.12.15; local testing used Python 3.12.14, both within the
specified Python 3.12 release. No failed CI reruns or code-repair retries were
needed after the original one-line repair. The subsequent documentation push
is a normal new PR synchronize event, not a rerun of a failed job.

The independent code review in the repository remains scoped to its stated
immutable SHA; all source/tests/workflow changes after it are empty. The PR
includes final post-CI verification separately. No formal approval from another
GitHub identity, branch-protection enforcement, merge, or deployment is claimed.

## Human intervention accounting

Counting begins after the original execution request. That request is one
initial input, separate from subsequent interventions.

- Additional user chat messages: **3** (status check, publication/wait update,
  and the current resume request).
- Human code edits or manual bug fixes observed: **0**.
- User-reported environment publication: **at least 1**. Exact environment UI
  action count cannot be independently observed and is not asserted to be zero.
  This action and the message reporting it are described separately rather than
  claiming an exact total of distinct human interventions.
- Codex performed implementation, failure diagnosis, repair, testing, Git pushes,
  Draft PR creation, CI inspection, and separate-context code review.
- The reviewer was another Codex context on the same managed environment, not
  another VM or human GitHub approver.
- No agent-driven environment publication, important permission change, purchase,
  merge, or deployment occurred during resumption. The user published the
  environment; API access was verified afterward.

This validates one bounded seeded-defect loop with human environment setup.
It does not prove zero-human end-to-end automation for arbitrary future specs,
and no agent is running inside Actions: GitHub Actions executes tests; Codex
performs the development and review work in its existing execution contexts.

## Local·Cloud 병렬 개발 및 통합 실험 — 2026-11-01

**독립 개발한 두 변경의 Git 통합, 실제 테스트·PR CI와 별도 문맥의 코드 리뷰를 완료했다.**
두 작업의 실행 시점은 겹쳤다고 입증할 수 없어 병렬 속도 향상은 주장하지 않는다.
이 절은 위의 이전 실험과 별도로 기록하며 기존 테스트·CI와 이 보고서를 재사용한다.

| 담당 | 공통 기준 SHA | 결과 브랜치 | 원본 결과 SHA |
| --- | --- | --- | --- |
| Local | `72b655ab542f1e8e552b26306a67b4bb099aad31` | `codex/local-range-format` | `783cee0ad715be5a483c7063158938f48b8fcc6e` |
| Cloud | 동일 | `codex/cloud-range-stats` | `f07210cdfd7f85edbb445a03bf0b874fb91e9b8b` |
| 통합 | 동일 | `codex/parallel-local-cloud` | 코드 SHA `024a8caa9b3f817608bc516021c2a2578ecdb2a4` |

작업 전과 통합 직전에 `origin/main`을 실제 fetch했고 공통 기준 SHA와 일치했다.
시작 시 작업 트리는 깨끗했다. Cloud 원본의 단일 부모도 기준 SHA와 일치한다.

### 분리한 작업과 Acceptance Criteria

- Local 담당: `range_summary.py`, `tests/test_range_formatting.py`.
  `format_ranges(values: Iterable[int]) -> str`가 기존 `coalesce_ranges()`를 재사용한다.
  빈 입력은 빈 문자열, `[3,1,2,2,6]`은 `1-3,6`, `[-3,-2,-1,2]`는 `-3--1,2`다.
  단일값은 정수 문자열, 범위는 `start-end`, 구분자는 공백 없는 쉼표다.
- Cloud 담당: `range_summary_stats.py`, `tests/test_range_stats.py`.
  `summarize_ranges(values: Iterable[int]) -> dict[str, int]`가 기존 함수를 import해 재사용한다.
  반환 키는 `value_count`(중복 제외 정수 개수), `range_count`(최대 연속 범위 개수)뿐이다.
  빈 입력은 0/0, `[3,1,2,2,6]`과 `[0,-2,-1,4]`는 4/2다. 범위를 직접 열거하지 않는다.
- 공통: 정렬·중복 제거, 단일값·음수·큰 정수, 한 번만 소비하는 iterable, 입력 보존,
  built-in int 이외 원소의 TypeError 계약을 검증한다. 기존 API·CLI·테스트·CI 계약을 유지한다.
- Cloud의 복사 가능한 전체 지시문은 [Local Draft PR #3](https://github.com/JinwooJeon1024/agent_workflow_lab/pull/3)에 보존했다.
  두 작업의 변경 파일은 겹치지 않으며 새 프레임워크·의존성·문서는 추가하지 않았다.

### Git 통합과 실제 테스트

초기 Local 구현 `124ff116479d8f82d2e388739bafdcb9bc69d8f8`과 보고서 초안은 통합 준비 브랜치에 이미 있었다.
독립 리뷰가 Python의 십진수 변환 제한을 넘는 `10**5000`에서 실패하는 P2를 발견했다.
Local 수정 1회로 전역 설정을 바꾸지 않는 chunk 변환과 회귀 테스트를 추가했다.

사용자의 명시 승인 후 다음 명령을 실행했다. 두 명령 모두 exit 0이며 `-x`로 원본 SHA를 보존했다.

```text
git switch codex/parallel-local-cloud
git cherry-pick -x 783cee0ad715be5a483c7063158938f48b8fcc6e
git cherry-pick -x f07210cdfd7f85edbb445a03bf0b874fb91e9b8b
```

적용된 Local 수정 SHA는 `a5a72f1bc540ee7718b7ed49bca78b65079fd07d`,
Cloud 적용 및 통합 코드 SHA는 `024a8caa9b3f817608bc516021c2a2578ecdb2a4`다.
각 담당 파일은 원본 Local/Cloud 결과와 `git diff --exit-code`로 정확히 일치함을 확인했다.

| 대상 | 실제 검증 | 결과 |
| --- | --- | --- |
| 기준 | `python3 -m unittest discover -s tests -v` | 16개, exit 0 |
| Local 원본 | `python3 -m unittest discover -s tests -p test_range_formatting.py -v`; 전체 suite | 9개 / 25개, exit 0 |
| Cloud 원본의 정확한 archive | `python3 -m unittest discover -s tests -p test_range_stats.py -v`; 전체 suite | 15개 / 31개, exit 0 |
| 통합 코드 SHA | `python3 -m unittest discover -s tests -v` | 40개, exit 0 (Python 3.12.1) |
| 통합 CLI | `python3 -m range_summary 3 1 2 2 6` | `[[1, 3], [6, 6]]`, exit 0 |
| 두 API smoke | 같은 프로세스에서 `1-3,6`과 `{"value_count": 4, "range_count": 2}` 확인 | exit 0 |
| 범위·보존 | `git diff --check`; 기존 테스트·CI에 대한 `git diff --exit-code` | exit 0 |

Cloud의 첫 로컬 스냅샷 검사에서는 Windows 임시 short path로의 디렉터리 이동이 실패해
유효 테스트를 실행하지 못했다. 이를 성공으로 집계하지 않았고 workspace의 ignored 임시
스냅샷에서 위의 15개/31개를 실제 재실행했다. 제품 코드 수정은 필요하지 않았다.

### 실제 GitHub Actions와 독립 리뷰

- 통합 결과: [Draft PR #4](https://github.com/JinwooJeon1024/agent_workflow_lab/pull/4), base `main`.
- [통합 코드 CI run 41215224814](https://github.com/JinwooJeon1024/agent_workflow_lab/actions/runs/41215224814):
  `pull_request`, head `024a8caa9b3f817608bc516021c2a2578ecdb2a4`,
  attempt 1, `completed/success`.
- [job 124578241031](https://github.com/JinwooJeon1024/agent_workflow_lab/actions/runs/41215224814/job/124578241031):
  표준 GitHub-hosted Ubuntu, CPython 3.12.15, 읽기 전용 Contents 권한.
  모든 step 성공이며 실제 로그의 `Ran 40 tests`, `OK`와 CLI assertion 성공을 확인했다.
  run 생성~완료 기록은 00:31:06~00:31:15 KST, 9초다.
- [Local 단독 CI run 41213172054](https://github.com/JinwooJeon1024/agent_workflow_lab/actions/runs/41213172054)는
  Local SHA의 25개 테스트 성공이다. Cloud 원본 브랜치에는 별도 PR CI가 없었으며,
  Local CI를 통합 CI의 증거로 대신하지 않았다.
- 구현 대화가 없는 새 Codex 문맥이 정확한 통합 코드 SHA의 archive를 검토했다.
  전체 40개 테스트와 독립 테스트 7개가 통과했다. 8,192개 부분집합·중복·역순 입력,
  seeded 무작위 1,000개, `±10**5000`, 엄격한 타입·one-shot·입력 보존·함수 재사용·CLI 계약,
  십진수 제한 640에서 전역 설정 변경 금지와 초대형 끝점 산술을 확인했다.
- 리뷰 결과: **발견사항 없음(P0–P3 0건)**. Local/Cloud 담당 파일의 원본 바이트 일치,
  기존 테스트·CI 바이트 불변과 `coalesce_ranges`·`main` AST 불변도 확인했다.
  archive SHA256: `635ae8c51e26bbdaaec885883260cb80bf9221426fdb20850b7e5b2d26cee375`.
- 원본 Local/Cloud도 각각 독립 리뷰를 통과했다. 새 문맥의 독립 실행은 로컬 archive 검증이며,
  원격 CI run/job/log는 주 작업 문맥에서 직접 조회했다.
- 이후 이 보고서만 갱신하는 커밋은 구현·테스트·CI와 분리한다.
  **최종 PR head SHA와 해당 최신 CI는 PR #4 본문에 기록한다.** 별도 GitHub 계정의 승인을 뜻하지 않는다.

### 사람 개입·대기·충돌 측정과 한계

- 관측 시작: 2026-11-01 00:00:28 KST (2026-10-31 15:00:28 UTC).
- 최초 요청 1회는 초기 입력으로 분리한다. 관측된 추가 사용자 메시지는 **3회**:
  Cloud 수동 실행 방식 지정, Cloud 완료 알림, 통합 cherry-pick 승인.
  승인 1회는 이 3회 안에 포함되며 중복 합산하지 않는다.
- Cloud에 별도 지시·수동 실행 **1회 이상**은 사용자 보고로 확인했다.
  정확한 추가 지시/UI 행동 수, Cloud 내부 수동 코드 수정 여부는 알 수 없어 0으로 가정하지 않는다.
  Local에서 관측된 사람의 수동 코드 수정은 0회다.
- 환경 확인 대기 관측 구간: 00:01:48~00:05:39 KST, 약 **3분 51초**.
  CLI에 `All Environments (Global)`만 보인 뒤 사용자 지시에 따라 조회·연동 탐색을 중단했다.
  Cloud Task는 사용자가 웹에서 수동 시작했다. 직접 생성 자동화는 별도 후속 과제다.
- 수동 방식 전환 확인(00:05:39)부터 Cloud 원격 결과 확인(00:21:13)까지 경과는 **15분 34초**다.
  사람 작업·Cloud 실행·통신 대기가 섞여 순수 대기 시간을 분리할 수 없다.
  Cloud 커밋 시각 00:19:43은 실제 작업 시작·완료 시각으로 간주하지 않는다.
- 통합 승인 대기 관측 구간: 00:23:23~00:29:58 KST, 약 **6분 35초**.
  최초 자동 승인 검토가 cherry-pick을 사용자의 병합 승인 조건으로 거부해 실행되지 않았다.
  이후 사용자가 두 cherry-pick을 명시 승인한 뒤 진행했으며 거부를 우회하지 않았다.
- 실제 통합 구간: 00:30:11.878~00:30:12.158 KST.
  두 cherry-pick의 stopwatch 처리 시간 **151ms**, 충돌 **0건**, 충돌 해결 시간 **0초**다.
- Local 코드 완료 후 Cloud 수동 실행으로 전환했으므로 실제 동시 개발을 입증하지 못했다.
  이번 결과는 파일·브랜치를 분리한 독립 개발과 통합 검증이며, 병렬 속도 향상이나 무인 자동화를 증명하지 않는다.
- 리뷰에 따른 Local 수정 1회, Cloud/통합 코드 수정 0회, 실패 CI 수동 재실행 0회다.
  보고서 갱신 push의 synchronize CI는 새 head의 정상 검증이며 실패 job 재실행이 아니다.
- 환경 생성·게시, 인증·권한·설정 변경, 배포, main 병합은 에이전트가 수행하지 않았다.
  통합 PR은 Draft로 유지하며 main 병합은 별도 사용자 승인 대상이다.

## 정수 차집합 Phase 2 재개

`5eb289c` 체크포인트에서 재개해 `difference_ranges`와 신규 테스트 20개를 구현했다.
전체 unittest 77개·명세 doctest 23개가 통과했고,
[Draft PR #6](https://github.com/JinwooJeon1024/agent_workflow_lab/pull/6)을 생성했다.
체크포인트→구현 SHA, 실제 CI·독립 리뷰, Phase 2 별도 측정과 한계는
[Phase 2 실행 보고서](difference-phase2-report.md)에 기록한다. PR은 병합하지 않는다.
