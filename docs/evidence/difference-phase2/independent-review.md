# Difference API Phase 2 독립 리뷰

검토일: 2026-11-01 (Asia/Seoul). 구현에 참여하지 않은 별도 에이전트 문맥에서 AGENTS.md, 검토 커밋의 docs/spec.md, 변경 diff, 기존 코드와 CI를 직접 읽고 검증했다.

## 판정과 범위

**P0–P3 발견사항 없음.** 검토한 차집합 계약, 기존 API·CLI 보존, 테스트 및 CI 범위에서 수정이 필요한 결함을 찾지 못했다.

- Reviewed SHA: `fc1d8a1ce189b225a431286b98daaa35ec35e84c`
- 체크포인트: `5eb289c2a216dd98a25031b33adb4916c4c7c40a`
- 체크포인트가 reviewed SHA의 조상임을 `git merge-base --is-ancestor`의 종료 0으로 확인했다.
- diff는 `range_summary.py` 수정과 `tests/test_range_difference.py` 추가 두 파일, 202줄 추가다. 기존 테스트, `range_summary_stats.py`, CLI, CI, 의존성, spec은 체크포인트와 동일하다.
- 구현·기존 테스트·CI 수정, 커밋, push, GitHub 메시지 게시를 수행하지 않았다. 리뷰 증거는 `independent-*` 파일에만 새로 작성했다.

| 우선순위 | 발견사항 |
| --- | --- |
| P0 | 없음 |
| P1 | 없음 |
| P2 | 없음 |
| P3 | 없음 |

## 정확한 스냅샷

작업 트리 대신 `git archive`로 reviewed SHA를 추출한 아래 디렉터리에서 Python 3.12.1로 검증했다. `.gitignore`의 `__pycache__/` 적용도 `git check-ignore`로 확인했다.

```text
__pycache__/difference-review/fc1d8a1ce189b225a431286b98daaa35ec35e84c/
```

Archive SHA256: `b052c8024ed15c8647a8a716c958fa63f935a664969fb50064b57a396d3a1e9e`

Snapshot manifest SHA256: `49521a406a8382cd48c35f8136cb4abfa3bb142d9038eed351d36bb748ec484d`

Manifest hash는 추출된 파일 40개의 상대 경로를 정렬한 다음 `<file SHA256>  <relative path>\n` 형식의 UTF-8 바이트를 SHA256한 값이다. 모든 검증 후 파일 40개 해시가 초기값과 같은지도 확인했다. 파일별 해시·경로·크기·archive 절대 경로는 [independent-snapshot.json](independent-snapshot.json)에 기록했다.

## 실행과 실제 결과

실행 파일은 `C:\Users\전진우\AppData\Local\Programs\Python\Python312\python3.exe`이며 버전 출력은 `Python 3.12.1`이다. 아래 Python 명령의 cwd는 위 스냅샷이다. Git 명령은 저장소 루트에서 실행했고, 매번 `C:\Program Files\Git\cmd\git.exe -c safe.directory=C:/Users/전진우/Documents/GitHub/agent_workflow_lab`를 사용했다. 전역 Git 설정은 변경하지 않았다.

| 실행 | 종료 상태 | 실제 결과 |
| --- | ---: | --- |
| `python3.exe docs/evidence/difference-phase2/independent-verify.py` (저장소 루트) | 0 | 스냅샷 생성과 아래 15개 subprocess 명령 완료, 검증 후 스냅샷 파일 40개 불변 |
| `python3.exe --version` | 0 | Python 3.12.1 |
| Git `rev-parse`, `merge-base --is-ancestor`, `check-ignore`, `archive`, `diff --name-status`, `diff --check`, `diff`, `show` | 각각 0 | SHA·계보·ignored 디렉터리·변경 범위·공백 오류·기존 코드 확인 |
| `python3.exe -m unittest discover -s tests -v` | 0 | **77 tests, OK** (기존 57개 + 새 차집합 테스트 20개) |
| `python3.exe -m doctest -v docs/spec.md` | 0 | **23 passed and 0 failed** |
| `python3.exe -m range_summary 3 1 2 2 6` | 0 | `[[1, 3], [6, 6]]` 및 줄바꿈 |
| `python3.exe -m range_summary` | 0 | `[]` 및 줄바꿈 |
| `python3.exe -m range_summary not-an-integer` | **2 (기대값)** | argparse invalid int 오류 |
| `python3.exe <독립 스크립트 절대 경로> --oracle <스냅샷 절대 경로>` | 0 | **276,244개 시나리오 통과** |

실제 argv, cwd, 시작·종료 시각, 종료 코드, stdout, stderr는 [independent-commands.json](independent-commands.json)에 보존했다. 별도 원문 로그는 [unittest](independent-unit-tests.log.gz), [doctest](independent-doctest.log.gz), [CLI 예제](independent-cli-example.log.gz), [빈 CLI](independent-cli-empty.log.gz), [잘못된 CLI](independent-cli-invalid.log.gz), [oracle](independent-oracle.log.gz), [Python 버전](independent-python-version.log.gz)에 있다. diff 원문은 공백을 보존해 [independent-reviewed-diff.log.gz](independent-reviewed-diff.log.gz)에 저장했다. 실행기 최종 결과는 [independent-result.json](independent-result.json)에 있다.

이 7개 실행 로그에는 Windows 출력 포장 중 생긴 CRCRLF가 있어 Git 공백 검사에서 지적되었다. 텍스트를 정규화하지 않고 `read_bytes()`로 읽은 원본 바이트를 `gzip.compress(..., mtime=0)`로 압축했으며, 압축 해제 결과가 원본과 같은지 확인했다. 원본·압축 SHA256, 바이트 수, CRCRLF 개수와 복원 일치는 [independent-packaging.json](independent-packaging.json)에 기록했다. CI JSON 4개의 EOF 빈 줄도 마지막 줄바꿈 하나로 정리하고 JSON 의미 동일성을 같은 파일에 기록했다. 이 포장 수정에서는 제품 코드·테스트·CI·검증 스크립트를 변경하거나 검증을 재실행하지 않았다.

독립 [검증 스크립트](independent-verify.py)는 구현의 coalesce·두 포인터 코드를 oracle로 사용하지 않는다. `sorted(set(left).difference(right))`에 `enumerate`와 `itertools.groupby`의 `value - index` 키를 적용해 최대 연속 구간을 별도로 구성한다. 전체 실행기는 기존 증거를 덮어쓰지 않도록 새 스냅샷 경로를 요구하며, 기존 스냅샷에서 oracle만 다시 실행할 때는 위 `--oracle` 명령을 쓸 수 있다.

| 독립 검증 범주 | 시나리오 수 |
| --- | ---: |
| 명시적 경계·방향·분할·전체 제거 | 15 |
| `[-4, 4]`의 모든 부분집합 쌍, 역순·중복 입력 | 262,144 |
| 고정 seed `20261101`의 무작위 입력 쌍 | 12,000 |
| 큰 정수 평행이동 입력 쌍 | 2,000 |
| 20,001개 정수 범위의 조밀한 분할·제거 | 2 |
| 좌→우 완전 소비, 독립 one-shot, 공유 iterator/list | 3 |
| bool·int 하위 클래스 등을 양쪽·빈 입력에서도 거부 | 66 |
| non-iterable 인자 거부 | 10 |
| 사용자 iterator 예외 전달 | 2 |
| 두 입력의 기존 `coalesce_ranges` 호출 순서·대상 확인 | 1 |
| 정규화 결과를 주입해 `10**5000` 규모 구간 내부 비확장 확인 | 1 |
| **합계** | **276,244** |

합계는 검증 시나리오 수이며 unittest test method 수나 개별 assert 수와 구분한다. 마지막 두 시나리오는 프로세스 내 함수를 일시 교체해 정규화 재사용과 구간 연산을 분리 검증하고 즉시 원복했다. 스냅샷 파일은 수정하지 않았다.

## 코드 검토 근거

`range_summary.py:69–70`은 왼쪽을 완전히 정규화한 후 오른쪽을 정규화한다. 따라서 오른쪽이 비어 있어도 왼쪽 원소를 검증하고, 왼쪽이 비어 있어도 오른쪽 원소를 검증한다. built-in int 검증과 단회 소비는 기존 `coalesce_ranges`를 그대로 사용한다. 공유 iterator를 복제하지 않는 동작도 계약과 일치한다.

`range_summary.py:74–92`는 정규화된 왼쪽 구간마다 오른쪽과 겹치지 않는 앞부분과 끝부분을 출력한다. 특히 `84–87`에서 오른쪽 구간이 현재 왼쪽 끝에 도달하면 포인터를 유지하여 이후 왼쪽 구간까지 덮는 경우를 처리한다. 오른쪽 포인터는 증가만 하고, 유지한 상태의 종료는 왼쪽 구간당 한 번이므로 정규화 후 구간 처리 시간은 O(L+R)이다. 숫자 사이의 값이나 공백을 나열하는 루프가 없으며 정규화가 전체 O(n log n + m log m) 시간과 O(n+m) 공간을 지배한다. 수치의 비트 길이에 따른 정수 연산 비용은 이 입력 개수 기준 표기와 별개다.

기존 `range_summary.py` AST와 새 함수를 제거한 reviewed AST도 동일했다. 새 테스트는 기존 discovery가 수집하며, 오류·큰 정수·단회 소비·공유 상태·구간 재사용·독립 작은 domain oracle을 포함한다. 기존 테스트의 약화나 삭제는 없다.

## 원격 CI 독립 확인

**실제 원격 CI를 독립 확인했다.** GitHub 연결의 읽기 도구로 아래 run 원본 JSON, job·step 요약과 실제 job 로그를 직접 조회했다.

- [Actions run 41223386481](https://github.com/JinwooJeon1024/agent_workflow_lab/actions/runs/41223386481), attempt 1, `event=pull_request`, `status=completed`, `conclusion=success`.
- 원본 run JSON의 `head_sha`는 reviewed SHA `fc1d8a1ce189b225a431286b98daaa35ec35e84c`와 같다. 연결된 PR은 [#6](https://github.com/JinwooJeon1024/agent_workflow_lab/pull/6), base는 `main`이다.
- Job `124602395300`, `Python 3.12 tests`가 성공했다. setup, checkout, Python setup, unittest, CLI, post/complete를 포함해 반환된 8개 step 모두 `completed/success`다.
- 실제 로그는 head SHA를 base `7fe9e7b7271478f9f0fbbd70486bc56e4c664cbb`에 합성한 merge commit checkout을 보여 준다. `Ran 77 tests in 0.379s`, `OK`, 문서화된 CLI 문자열 비교를 확인했다.
- workflow는 기존 `pull_request` 트리거, `ubuntu-latest`, Python 3.12, `permissions: contents: read`, SHA 고정 checkout/setup-python, credentials 비보존, unittest와 CLI 검증을 유지한다. CI에서 doctest·독립 oracle을 실행했다고 해석하지 않는다. 그 두 검증은 위 로컬 스냅샷에서 실행했다.

조회 도구·인자는 [independent-ci-requests.json](independent-ci-requests.json), 원본 run JSON은 [independent-ci-run.json](independent-ci-run.json), job/step 결과는 [independent-ci-jobs.json](independent-ci-jobs.json) 및 [independent-ci-steps.json](independent-ci-steps.json)에 보존했다. [실제 job 로그](independent-ci-job.log.gz)는 원문의 줄끝 공백을 보존하기 위해 gzip으로 저장했고, 압축 전후 해시 및 복원 일치는 [independent-ci-log-hashes.json](independent-ci-log-hashes.json)에 기록했다.

이 판정은 명시한 reviewed SHA와 해당 run에 한정한다. 이후 증거·문서 커밋이나 최신 PR head의 CI 성공은 이 리뷰의 확인 범위에 포함하지 않는다.
