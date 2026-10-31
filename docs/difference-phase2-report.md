# difference_ranges Phase 2 실행 보고서

## 재개 지점과 결과

`codex/difference-ranges-checkpoint`의 계획된 중단 지점에서 Phase 2를 재개했다.
처음 확인한 작업 트리는 깨끗했고, fetch 후에도 아래 기준과 원격 체크포인트가 일치했다.
Phase 1의 명세 작성이나 이전 실험의 의도적인 결함 주입을 반복하지 않았다.

| 구분 | SHA |
| --- | --- |
| Phase 1 기준 `origin/main` | `7fe9e7b7271478f9f0fbbd70486bc56e4c664cbb` |
| Phase 1 체크포인트 | `5eb289c2a216dd98a25031b33adb4916c4c7c40a` |
| Phase 2 구현·테스트 및 독립 리뷰 대상 | `fc1d8a1ce189b225a431286b98daaa35ec35e84c` |

체크포인트는 명세만 변경했고 API·테스트·PR은 없는 상태였다. 기존 브랜치와
로컬 `main`을 그대로 보존하고 같은 체크포인트 브랜치에 구현을 추가했다.
[Draft PR #6](https://github.com/JinwooJeon1024/agent_workflow_lab/pull/6)의 대상은
`main`이며 병합하지 않는다. 구현 이후 보고서·증거 커밋은 제품 코드와 분리한다.
자기 SHA를 문서에 중복 저장하지 않도록 **최종 PR head와 해당 최신 CI는 PR 본문에 기록한다.**

## 구현과 보존

`difference_ranges(left, right)`는 왼쪽 정수 집합에서 오른쪽 값을 뺀 결과를
정렬된 최대 포함 구간으로 반환한다. 예를 들어 `[0, 1, 2, 3, 4]`, `[2]`는
`[(0, 1), (3, 4)]`가 된다.

기존 `coalesce_ranges`를 왼쪽, 오른쪽 순서로 호출해 각 입력을 한 번 소비·검증한다.
그 뒤 왼쪽 잔여 시작점과 단조 증가하는 오른쪽 포인터로 구간을 뺀다. 오른쪽 구간이
여러 왼쪽 구간에 걸치면 포인터를 유지한다. 값 사이의 간격을 정수로 확장하지 않으며,
정규화를 포함한 예상 시간은 O(n log n + m log m), 공간은 O(n+m)이다.

bool·int 하위 클래스·그 밖의 잘못된 원소를 결과나 반대쪽의 빈 입력과 관계없이
거부한다. 입력 컬렉션은 바꾸지 않으며 공유 iterator 상태는 복제하지 않는다.
새 CLI 옵션이나 의존성은 없다. 기존 함수·CLI, 기존 테스트 4개 파일, CI 설정,
`range_summary_stats.py`, Phase 1 명세를 보존했다.

## 로컬 검증

실제 실행 기록은 [local-checks.json](evidence/difference-phase2/local-checks.json)에 있다.
아래 Python 명령은 모두 로컬 CPython **3.12.1** 실행 파일로 수행했다.

| 검증 | 실제 결과 | 증거 |
| --- | --- | --- |
| 구현 전 `python3 -m unittest discover -s tests -v` | 기존 57개 통과, exit 0 | [기준 로그](evidence/difference-phase2/baseline-unittest.log) |
| `python3 -m doctest -v docs/spec.md` | 23개 통과, exit 0 | [doctest 로그](evidence/difference-phase2/doctest.log) |
| `python3 -m unittest discover -s tests -v` | 기존 57개 + 신규 20개 = 77개 통과, exit 0 | [unittest 로그](evidence/difference-phase2/unittest.log) |
| `python3 -m range_summary 3 1 2 2 6` | 정확한 `[[1, 3], [6, 6]]`와 줄바꿈, 빈 stderr, exit 0 | [CLI 로그](evidence/difference-phase2/cli.log) |
| `git diff --check` | exit 0 | [결과](evidence/difference-phase2/diff-check.log) |
| 체크포인트 대비 기존 테스트·명세·CI·stats 파일 `git diff --exit-code` | exit 0 | [결과](evidence/difference-phase2/preserved-files.log) |

신규 unittest는 비대칭 차집합·빈 입력·중복·음수·끝점 제거·한 구간의 여러 분할·여러
왼쪽 구간에 걸친 오른쪽 구간·`±10**5000`·단회 소비·공유 iterator·입력 보존·엄격한 타입을
검사한다. `-3..3`의 모든 부분집합 쌍 **16,384건**을 역순·중복 입력으로 만들어
구간 경계 기반 독립 oracle과 대조한다. 이는 20개 unittest 중 한 테스트 내부의
subTest 개수이며 unittest 총수에 더하지 않는다.

초기 런타임 확인 중 기본 Python 3.13.15에서도 기존 57개가 통과했으며
[별도 로그](evidence/difference-phase2/baseline-python313-unittest.log)로 남겼다.
Python 3.12 실행 파일 위치를 확인한 뒤 계약에 맞는 3.12.1로 위 기준 검증을 수행했다.
환경 설치나 영구 설정 변경은 하지 않았다.

## 실제 GitHub Actions

- [구현 커밋 run 41223386481](https://github.com/JinwooJeon1024/agent_workflow_lab/actions/runs/41223386481):
  `pull_request`, head `fc1d8a1ce189b225a431286b98daaa35ec35e84c`,
  attempt 1, `completed/success`.
- [job 124602395300](https://github.com/JinwooJeon1024/agent_workflow_lab/actions/runs/41223386481/job/124602395300):
  `Python 3.12 tests`, 모든 step `completed/success`.
- 실제 로그는 GitHub-hosted Ubuntu 26.04.1, CPython 3.12.15, 읽기 전용 Contents 권한과
  PR merge commit `5d114ba`의 checkout을 보여 준다. merge checkout은 구현 head와 위 main 기준의
  조합이다. 로그의 `Ran 77 tests`, `OK`와 CLI assertion 성공을 직접 확인했다.
- run 생성~완료: **2026-11-01 02:12:19~02:12:26 KST**, 7초.
- 증거: [원본 run 메타데이터](evidence/difference-phase2/ci-implementation-run.json),
  [run 요약](evidence/difference-phase2/ci-implementation-runs.json),
  [job/step 결과](evidence/difference-phase2/ci-implementation-jobs.json),
  [원본 job 로그 gzip](evidence/difference-phase2/ci-implementation-job.log.gz).

원격 CI는 unittest와 기존 CLI를 실행한다. 명세 doctest는 로컬 및 독립 리뷰에서
별도로 검증했다. 로컬 성공을 원격 CI 성공의 증거로 대체하지 않았다.
이 보고서와 증거만 추가한 최신 head의 CI 결과도 PR 본문에서 확인할 수 있다.

## 독립 리뷰

구현 대화를 전달받지 않은 별도 Codex 문맥이 정확한 구현 커밋의 archive에서
명세·diff·코드·테스트·CI를 검토했다. 판정은 **P0–P3 발견사항 없음**이다.
전체 unittest 77개·doctest 23개와 추가 독립 검증 **276,244건**이 통과했다.
독립 검증에는 부분집합 쌍 262,144개, 고정 seed 난수 12,000개, 큰 정수 평행이동
2,000개와 소비·타입·정규화 재사용·구간 비확장 검증 등이 포함된다.
리뷰어도 위 구현 SHA의 원격 run·event·head SHA·job/step·실제 로그를 직접 확인했다.

Archive SHA256: `b052c8024ed15c8647a8a716c958fa63f935a664969fb50064b57a396d3a1e9e`.
기존 API·CLI의 AST 보존과 스냅샷 파일 40개의 실행 전후 해시 일치도 확인했다.
실행 명령·스냅샷 해시·발견사항과 한계는
[독립 리뷰 보고서](evidence/difference-phase2/independent-review.md)에 기록했다.
이후 보고서·증거만 추가한 커밋은 이 구현 리뷰 범위와 구분한다.

## Phase 2 측정과 한계

- Phase 2 첫 증거 파일 생성: **2026-11-01 02:11:01.783 KST**.
  [원본 시각](evidence/difference-phase2/started-at.txt). 구현 커밋 시각은 02:11:51 KST다.
  Phase 1 시간과 합산하지 않으며 커밋 시각을 전체 실행 종료 시각으로 간주하지 않는다.
- 이번 명시적 재개 요청은 최초 입력 1회다. 이후 관측된 추가 사람 지시·승인·수동 코드 수정은
  **0회**다. 보이지 않는 사람의 설정·행동은 알 수 없으며 0으로 가정하지 않는다.
- 실패 후 제품 코드 repair **0/3회**, 테스트 약화·skip·expected failure 전환 **0회**.
  이전 실험의 결함 주입·repair 횟수는 Phase 2에 중복 합산하지 않는다.
- 최종 staging 공백 검사에서 일부 독립 로그의 Windows 줄바꿈과 JSON의 여분 끝줄을
  발견해 증거 형식만 정리했다. 로그는 원문 바이트를 gzip으로 보존하고 JSON 데이터는
  유지했다. 이 증거 패키징 수정은 제품 코드 repair와 구분한다.
- 실패 CI 재실행 **0회**. 보고서 추가 push에 따른 synchronize 실행은 새 head 검증이다.
- Git 실행 파일 위치와 명령별 `safe.directory` 인자로 로컬 확인을 진행했다.
  전역 Git 설정·저장소 권한·환경·인증·배포를 변경하지 않았고 PR 병합도 하지 않았다.
- 이는 계획된 중단 후 명시적 지시로 재개한 한 번의 실행이다. 실제 프로세스 충돌 복구,
  무인 재시작, 일반적인 자동 복구 성능이나 별도 GitHub 계정의 승인을 입증하지 않는다.
